import os
import json
import asyncio
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root_dir, 'backend'))

from vigileye.agents.spatial_reasoning import spatial_agent
from vigileye.topology import get_neighbors, get_arrival_window
from vigileye.search import cosine_similarity

async def run_diagnostics():
    db_path = os.path.join(root_dir, 'data', 'cache', 'tracks_db.json')
    with open(db_path, 'r') as f:
        tracks = json.load(f)
        
    agreement_detail = []
    
    for t in tracks:
        query_emb = t['embedding']
        cam_id = t['camera_id']
        start_ts = t['first_ts']
        query_track_id = t['track_id']
        
        # We need the ground truth brute force top match (on a different camera)
        bf_matches = []
        for other_t in tracks:
            if other_t['camera_id'] != cam_id:
                sim = cosine_similarity(query_emb, other_t['embedding'])
                if sim >= 0.09: # REID_THRESHOLD
                    bf_matches.append({
                        "track_id": other_t['track_id'],
                        "camera_id": other_t['camera_id'],
                        "timestamp": other_t['first_ts'],
                        "similarity": sim,
                        "class": other_t['class']
                    })
        
        bf_top = None
        if bf_matches:
            bf_top = max(bf_matches, key=lambda x: x["similarity"])
            
        # Handoff match
        ho_trail, ho_metrics = await spatial_agent.execute_trace(query_emb, cam_id, start_ts, mode="handoff")
        ho_top = None
        # trail[0] is the start camera, trail[1] is the handoff match if any
        if len(ho_trail) > 1:
            ho_track_id = ho_trail[1]['track_id']
            # Find the similarity of this match from bf_matches (or recalculate)
            ho_sim = ho_trail[1]['confidence'] / 100.0
            ho_top = {
                "track_id": ho_track_id,
                "camera_id": ho_trail[1]['camera_id'],
                "timestamp": ho_trail[1]['timestamp'],
                "similarity": ho_sim
            }
            
        # Compare
        agrees = False
        if bf_top and ho_top and bf_top['track_id'] == ho_top['track_id']:
            agrees = True
            
        category = "agreed"
        if not agrees:
            if bf_top is None:
                # No match found by BF either, so if HO also found none, they agree on None!
                if ho_top is None:
                    agrees = True
                    category = "agreed_none"
                else:
                    category = "ho_found_noise"
            else:
                # BF found a match, HO did not, or HO found a different one
                # Check if bf_top is a true match or noise.
                # Since we don't have explicit ground truth labels across cameras, we define
                # case (c) as: brute force matched a track but its class doesn't match the query's class
                # Wait, YOLO class is just "person" for all tracks. So we can't use class!
                # The user said: "the query track has no real match in the database (a query that appears in only one segment) and brute-force's "top match" is just noise above threshold".
                # How do we know if there is a real match? Maybe we can't know for sure, but we can check if the BF top match was in the topological window.
                # Let's check topological window for bf_top
                neighbors = get_neighbors(cam_id)
                if bf_top['camera_id'] in neighbors:
                    stats = neighbors[bf_top['camera_id']]
                    min_t, max_t = get_arrival_window(start_ts, stats["mean"], stats["std"])
                    if min_t <= bf_top['timestamp'] <= max_t:
                        category = "b_inside_window_but_different_score_or_threshold"
                    else:
                        category = "a_outside_window"
                else:
                    category = "a_not_a_neighbor"
                    
        # BUT wait! What about case (c)? The user says:
        # "the query track has no real match in the database... and brute-force's "top match" is just noise... which handoff correctly ignoring is NOT a disagreement to worry about - separate these out."
        # If the BF top match is outside the window, how do we know if it's case (a) transit prior too narrow, or case (c) just noise?
        # Let's look at the dataset properties. The video was 49.67s split into 3 segments (e.g. 16.5s each).
        # Transit time between cam_1 and cam_2 should be near-zero (since they are adjacent segments of one video).
        # Let's log transit times of BF top matches to see.
        transit_time = bf_top['timestamp'] - start_ts if bf_top else None
        
        detail = {
            "query_track": query_track_id,
            "query_camera": cam_id,
            "query_ts": start_ts,
            "bf_top": bf_top,
            "ho_top": ho_top,
            "agrees": agrees,
            "category": category,
            "transit_time": transit_time
        }
        agreement_detail.append(detail)
        
    with open(os.path.join(root_dir, 'benchmarks', 'agreement_detail.json'), 'w') as f:
        json.dump(agreement_detail, f, indent=2)
        
    print("Diagnosis complete.")
    for d in agreement_detail:
        print(f"Q: {d['query_track']} | BF: {d['bf_top']['track_id'] if d['bf_top'] else None} | HO: {d['ho_top']['track_id'] if d['ho_top'] else None} | Agree: {d['agrees']} | Cat: {d['category']} | Transit: {d['transit_time']}")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
