import os
import json
from fastapi import APIRouter
from vigileye.topology import TOPOLOGY

router = APIRouter()

@router.get("/")
async def get_metrics():
    # Attempt to load quantization benchmarks
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    benchmarks_path = os.path.join(root_dir, 'benchmarks', 'quantize_results.json')
    
    quant_results = {}
    if os.path.exists(benchmarks_path):
        with open(benchmarks_path, 'r') as f:
            quant_results = json.load(f)
            
    return {
        "quantization": quant_results,
        "learned_priors": TOPOLOGY
    }
