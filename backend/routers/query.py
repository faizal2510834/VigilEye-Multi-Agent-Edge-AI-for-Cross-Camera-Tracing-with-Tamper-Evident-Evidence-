from fastapi import APIRouter
from pydantic import BaseModel
from vigileye.agents.intent_parsing import intent_parser
from vigileye.agents.crypto_audit import crypto_agent

import torch
import numpy as np

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    justification: str
    operator_id: str = "demo_operator"

# Lazy load CLIP model
clip_model = None
tokenizer = None

def get_text_embedding(text: str):
    global clip_model, tokenizer
    try:
        import open_clip
        if clip_model is None:
            print("Loading OpenCLIP for text search...")
            clip_model, _, _ = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai', device='cpu')
            tokenizer = open_clip.get_tokenizer('ViT-B-32')
            
        tokens = tokenizer([text])
        with torch.no_grad():
            text_features = clip_model.encode_text(tokens)
            # Normalize
            text_features /= text_features.norm(dim=-1, keepdim=True)
            clip_emb = text_features.cpu().numpy().flatten()
            
            # The tracks DB uses 512 clip + 512 hsv = 1024 dims.
            # We'll pad with zeros for the HSV part.
            hsv_pad = np.zeros(512, dtype=np.float32)
            fused = np.concatenate([clip_emb, hsv_pad])
            return fused.tolist()
    except Exception as e:
        print(f"Failed to run CLIP text encode: {e}")
        # fallback to dummy 1024-dim if open_clip not available
        return [0.0] * 1024

@router.post("/")
async def parse_query(request: QueryRequest):
    # 1. Log query
    await crypto_agent.log_query(request.operator_id, request.justification, request.query)
    
    # 2. Parse intent
    parsed = intent_parser.parse_query(request.query)
    
    # 3. Get CLIP text embedding
    query_embedding = get_text_embedding(request.query)
    
    return {
        "parsed": parsed,
        "query_embedding": query_embedding
    }
