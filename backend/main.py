from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import routers.query
import routers.tracks
import routers.trace
import routers.metrics
import routers.evidence
import routers.agents
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load cached data on startup
    from vigileye.perception import TRACKS_DB
    print(f"Loaded {len(TRACKS_DB)} cached tracks.")
    yield
    print("Shutting down.")

app = FastAPI(title="VigilEye Demo API", lifespan=lifespan)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.query.router, prefix="/api/query", tags=["Query"])
app.include_router(routers.tracks.router, prefix="/api/tracks", tags=["Tracks"])
app.include_router(routers.trace.router, prefix="/api/trace", tags=["Trace"])
app.include_router(routers.metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(routers.evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(routers.agents.router, prefix="/api/agents", tags=["Agents"])

@app.get("/health")
def health():
    return {"status": "ok"}
