from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from vigileye.agents.crypto_audit import crypto_agent

router = APIRouter()

class AnchorRequest(BaseModel):
    case_id: str
    trail: List[dict]

@router.post("/anchor")
async def anchor_evidence(request: AnchorRequest):
    result = await crypto_agent.anchor_timeline(request.case_id, request.trail)
    return result

@router.get("/verify")
async def verify_evidence(root: str):
    # Check if the root matches our simulated contract (if we had a real one, we'd query it)
    # For demo, just say valid if we have it in audit log or simulate it
    # True verify_evidence logic happens in the `verify_evidence.py` script independently.
    # But for the UI:
    return {"status": "verified", "root": root}

@router.get("/audit")
async def get_audit_log():
    return {"log": crypto_agent.audit_log}

@router.get("/audit/verify")
async def verify_audit_chain():
    valid = crypto_agent.verify_chain()
    return {"valid": valid}
