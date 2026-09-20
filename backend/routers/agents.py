from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from vigileye.agents.bus import bus
import asyncio
import json

router = APIRouter()

@router.get("/feed")
async def get_agent_feed():
    return {"history": bus.message_history}

@router.get("/ws")
async def stream_agent_events():
    async def event_generator():
        queue = asyncio.Queue()
        
        # Callback to push to the queue
        async def on_event(msg):
            await queue.put(msg)
            
        bus.subscribe("AGENT_LOG", on_event)
        
        try:
            while True:
                msg = await queue.get()
                yield f"data: {json.dumps(msg)}\n\n"
        except asyncio.CancelledError:
            # Client disconnected
            pass
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
