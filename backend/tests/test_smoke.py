import asyncio
import pytest
from vigileye.agents.spatial_reasoning import spatial_agent
from vigileye.agents.crypto_audit import crypto_agent

def test_smoke_trace_and_evidence():
    print("\n--- Running Smoke Test ---")
    
    async def run_test():
        # 1. Trace Target
        # Dummy embedding for testing
        dummy_embedding = [0.1] * 1024
        trail, metrics = await spatial_agent.execute_trace(dummy_embedding, "cam_1", 0.0, mode="handoff")
        
        assert "inference_calls" in metrics
        print(f"Handoff Trace Completed. Trail length: {len(trail)}")
        print(f"Metrics: {metrics}")
        
        # 2. Evidence Anchor
        case_id = "smoke_case_001"
        evidence_res = await crypto_agent.anchor_timeline(case_id, trail)
        
        assert "merkle_root" in evidence_res
        print(f"Evidence Root: {evidence_res['merkle_root']}")
        print(f"Simulated Tx Hash: {evidence_res['tx_hash']}")
        
        # 3. Audit Log
        await crypto_agent.log_query("smoke_admin", "Smoke testing", "Find target")
        assert crypto_agent.verify_chain() == True
        print("Audit chain verified.")
        
    asyncio.run(run_test())

