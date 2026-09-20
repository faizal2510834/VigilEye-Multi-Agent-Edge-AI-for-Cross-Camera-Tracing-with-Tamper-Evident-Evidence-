from fastapi import APIRouter, HTTPException
from vigileye.perception import get_tracks_by_camera, TRACKS_DB

router = APIRouter()

@router.get("/")
async def get_tracks(camera_id: str = None):
    if camera_id:
        return {"tracks": get_tracks_by_camera(camera_id)}
    return {"tracks": TRACKS_DB}
