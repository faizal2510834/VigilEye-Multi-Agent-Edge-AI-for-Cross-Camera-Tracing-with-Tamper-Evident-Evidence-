import json
import os

def load_cached_tracks():
    """
    Loads tracks from the precomputed cache.
    In a real scenario, this is where ONNX YOLO+OSNet would process live RTSP streams.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    cache_file = os.path.join(root_dir, 'data', 'cache', 'tracks_db.json')
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return []

# Simulating an in-memory database of all perceived tracks
TRACKS_DB = load_cached_tracks()

def get_tracks_by_camera(camera_id):
    return [t for t in TRACKS_DB if t["camera_id"] == camera_id]

def get_track_by_id(track_id):
    for t in TRACKS_DB:
        if t["track_id"] == track_id:
            return t
    return None
