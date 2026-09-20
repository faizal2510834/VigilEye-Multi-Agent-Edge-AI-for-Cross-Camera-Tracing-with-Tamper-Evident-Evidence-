from fastapi import APIRouter, HTTPException
from vigileye.perception import get_tracks_by_camera, TRACKS_DB

router = APIRouter()

@router.get("/")
async def get_tracks(camera_id: str = None):
    if camera_id:
        tracks = get_tracks_by_camera(camera_id)
    else:
        tracks = TRACKS_DB
    return {"tracks": [t for t in tracks if t["track_id"].endswith("_early")]}
