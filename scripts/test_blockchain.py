import sys
import os
import asyncio

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(root_dir)

from vigileye.agents.crypto_audit import crypto_agent

async def test_real_blockchain():
    print("Testing real blockchain anchoring with Hardhat local node...")
    
    import uuid
    import time
    case_id = f"test_case_{uuid.uuid4().hex[:6]}"
    dummy_trail = [
        {"camera_id": "cam_1", "track_id": 4, "timestamp": int(time.time())},
        {"camera_id": "cam_2", "track_id": 15, "timestamp": int(time.time()) + 15}
    ]
    
    # Check connection
    if not crypto_agent.w3.is_connected():
        print("ERROR: Not connected to Hardhat node!")
        return
        
    print(f"Connected to node: {crypto_agent.w3.provider.endpoint_uri}")
    print(f"Contract address: {crypto_agent.contract.address if crypto_agent.contract else 'Not Loaded'}")
    
    print("\nAnchoring trail to blockchain...")
    result = await crypto_agent.anchor_timeline(case_id, dummy_trail)
    
    print(f"Merkle Root: {result['merkle_root']}")
    print(f"Transaction Hash: {result['tx_hash']}")
    print(f"Block Number: {result['block_number']}")
    
    if result["tx_hash"] != "simulated_tx_hash":
        print("\nVerifying evidence on-chain...")
        
        verification = crypto_agent.verify_evidence(result['merkle_root'])
        
        print(f"Verification Result: {verification}")
        
        if verification.get("exists"):
            print("\nSUCCESS: Real blockchain anchoring and verification complete!")
        else:
            print("\nFAIL: Evidence not found or verification failed.")
    else:
        print("\nFAIL: It still simulated the transaction.")

if __name__ == "__main__":
    asyncio.run(test_real_blockchain())
