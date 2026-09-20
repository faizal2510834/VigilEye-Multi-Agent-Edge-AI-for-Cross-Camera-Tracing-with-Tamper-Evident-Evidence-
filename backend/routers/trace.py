from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from vigileye.agents.spatial_reasoning import spatial_agent
from vigileye.perception import get_track_by_id

router = APIRouter()

class TraceRequest(BaseModel):
    track_id: Optional[str] = None
    query_embedding: Optional[list] = None
    start_camera: Optional[str] = "cam_1"
    start_time: Optional[float] = 0.0
    mode: str = "handoff" # handoff or brute_force

@router.post("/")
async def do_trace(request: TraceRequest):
    emb = request.query_embedding
    if request.track_id:
        track = get_track_by_id(request.track_id)
        if track:
            emb = track["embedding"]
            request.start_camera = track["camera_id"]
            request.start_time = track["first_ts"]
            
    if not emb:
        raise HTTPException(status_code=400, detail="Must provide track_id or query_embedding")
        
    trail, metrics = await spatial_agent.execute_trace(
        query_embedding=emb, 
        start_camera=request.start_camera, 
        start_time=request.start_time,
        mode=request.mode
    )
    
    return {
        "mode": request.mode,
        "trail": trail,
        "metrics": metrics
    }
