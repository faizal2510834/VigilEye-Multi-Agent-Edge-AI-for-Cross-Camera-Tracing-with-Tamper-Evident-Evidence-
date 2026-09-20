import os
from pydantic_settings import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    port: int = 8000
    host: str = "0.0.0.0"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Blockchain
    rpc_url: str = "http://127.0.0.1:8545" # default hardhat local node
    private_key: str = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80" # hardhat account 0
    
    # LLM
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = ""
    
    predictive_handoff_enabled: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Topology graph: adjacency list of camera_ids and base transit time (mean, std in seconds)
# In a real app this is dynamically updated. Here it's seeded.
TOPOLOGY = {
    "cam_1": {"cam_2": {"mean": 16.0, "std": 10.0}, "cam_3": {"mean": 32.0, "std": 10.0}},
    "cam_2": {"cam_1": {"mean": 16.0, "std": 10.0}, "cam_3": {"mean": 16.0, "std": 10.0}},
    "cam_3": {"cam_1": {"mean": 32.0, "std": 10.0}, "cam_2": {"mean": 16.0, "std": 10.0}}
}

# Similarity threshold (computed midpoint between same:0.24 and diff:-0.06)
REID_THRESHOLD = 0.09
