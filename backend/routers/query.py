from fastapi import APIRouter
from pydantic import BaseModel
from vigileye.agents.intent_parsing import intent_parser
from vigileye.agents.crypto_audit import crypto_agent

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    justification: str
    operator_id: str = "demo_operator"

@router.post("/")
async def parse_query(request: QueryRequest):
    # 1. Log query
    await crypto_agent.log_query(request.operator_id, request.justification, request.query)
    
    # 2. Parse intent
    parsed = intent_parser.parse_query(request.query)
    return {"parsed": parsed}
