from vigileye.search import search_embeddings, cosine_similarity
from vigileye.topology import get_neighbors, get_arrival_window
from vigileye.perception import get_tracks_by_camera, TRACKS_DB
from .bus import bus
from config import settings, REID_THRESHOLD
import asyncio

class SpatialReasoningAgent:
    def __init__(self):
        self.metrics = {
            "handoff": {"inference_calls": 0, "comparisons": 0},
            "brute_force": {"inference_calls": 0, "comparisons": 0}
        }
        
    def reset_metrics(self):
        self.metrics = {
            "handoff": {"inference_calls": 0, "comparisons": 0},
            "brute_force": {"inference_calls": 0, "comparisons": 0}
        }

    async def execute_trace(self, query_embedding, start_camera, start_time, mode="handoff", query_track_id=None):
        self.reset_metrics()
        if mode == "handoff":
            return await self._trace_handoff(query_embedding, start_camera, start_time, query_track_id)
        else:
            return await self._trace_brute_force(query_embedding, query_track_id)

    async def _trace_brute_force(self, query_embedding, query_track_id=None):
        await bus.publish("AGENT_LOG", {"agent": "Spatial", "msg": "Starting BRUTE FORCE search across all cameras."})
        trail = []
        
        q_base = None
        if query_track_id:
            q_base = "_".join(query_track_id.split("_")[:3])
            
        for track in TRACKS_DB:
            if q_base:
                c_base = "_".join(track.get("track_id", "").split("_")[:3])
                if q_base == c_base:
                    continue
                    
            self.metrics["brute_force"]["inference_calls"] += 1
            self.metrics["brute_force"]["comparisons"] += 1
            sim = cosine_similarity(query_embedding, track["embedding"])
            if sim >= REID_THRESHOLD:
                conf = sim * 100
                trail.append({
                    "camera_id": track["camera_id"],
                    "track_id": track["track_id"],
                    "timestamp": track["first_ts"],
                    "confidence": conf,
                    "explanation": f"Brute force match: similarity {sim:.2f}. Confidence {conf:.1f}%",
                    "crop_path": track.get("crop_path")
                })
        # Sort chronologically
        trail.sort(key=lambda x: x["timestamp"])
        return trail, self.metrics["brute_force"]

    async def _trace_handoff(self, query_embedding, start_camera, start_time, query_track_id=None):
        await bus.publish("AGENT_LOG", {"agent": "Spatial", "msg": f"Starting PREDICTIVE HANDOFF trace from {start_camera}."})
        trail = []
        
        # Initial search in start camera to find the baseline track
        cam_tracks = get_tracks_by_camera(start_camera)
        matches = search_embeddings(query_embedding, cam_tracks, threshold=REID_THRESHOLD, query_track_id=query_track_id)
        self.metrics["handoff"]["inference_calls"] += len(cam_tracks)
        self.metrics["handoff"]["comparisons"] += len(cam_tracks)
        
        current_camera = start_camera
        current_exit_time = start_time
        
        if matches:
            best = matches[0]["track"]
            current_exit_time = best["first_ts"]
            sim = matches[0]["similarity"]
            conf = sim * 100
            trail.append({
                "camera_id": current_camera,
                "track_id": best["track_id"],
                "timestamp": current_exit_time,
                "confidence": conf,
                "explanation": f"Initial match: similarity {sim:.2f}. Confidence {conf:.1f}%",
                "crop_path": best.get("crop_path")
            })

        # Handoff loop
        visited = set([current_camera])
        while True:
            neighbors = get_neighbors(current_camera)
            best_next_match = None
            best_sim = 0
            
            for neighbor_id, stats in neighbors.items():
                if neighbor_id in visited: continue
                
                min_t, max_t = get_arrival_window(current_exit_time, stats["mean"], stats["std"])
                await bus.publish("AGENT_LOG", {
                    "agent": "Spatial", 
                    "msg": f"Commanding {neighbor_id} to wake between {min_t:.1f}s and {max_t:.1f}s."
                })
                
                # Filter tracks in neighbor within window
                neighbor_tracks = get_tracks_by_camera(neighbor_id)
                # In real life, only frames in the window get sent to OSNet (inference_calls)
                # But we compare against all detections in that window
                candidates = [t for t in neighbor_tracks if min_t <= t["first_ts"] <= max_t]
                
                self.metrics["handoff"]["inference_calls"] += len(candidates)
                self.metrics["handoff"]["comparisons"] += len(candidates)
                
                n_matches = search_embeddings(query_embedding, candidates, threshold=REID_THRESHOLD, query_track_id=query_track_id)
                if n_matches and n_matches[0]["similarity"] > best_sim:
                    best_sim = n_matches[0]["similarity"]
                    best_next_match = n_matches[0]["track"]
                    best_camera = neighbor_id
                    
            if best_next_match:
                transit_time = best_next_match["first_ts"] - current_exit_time
                conf = best_sim * 100
                explanation = f"Predictive match: similarity {best_sim:.2f}, transit {transit_time:.1f}s within expected window. Confidence {conf:.1f}%"
                
                trail.append({
                    "camera_id": best_camera,
                    "track_id": best_next_match["track_id"],
                    "timestamp": best_next_match["first_ts"],
                    "confidence": conf,
                    "explanation": explanation,
                    "crop_path": best_next_match.get("crop_path")
                })
                current_camera = best_camera
                current_exit_time = best_next_match["first_ts"]
                visited.add(current_camera)
                
                await bus.publish("AGENT_LOG", {"agent": "Spatial", "msg": f"Handoff successful to {current_camera} at {current_exit_time:.1f}s."})
            else:
                await bus.publish("AGENT_LOG", {"agent": "Spatial", "msg": "Trail lost. No matches in predicted windows."})
                break
                
        return trail, self.metrics["handoff"]

spatial_agent = SpatialReasoningAgent()
