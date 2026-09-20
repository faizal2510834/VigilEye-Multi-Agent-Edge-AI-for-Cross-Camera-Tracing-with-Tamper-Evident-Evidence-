import hashlib
import json
import time
from web3 import Web3
from config import settings
from .bus import bus
import os

class CryptoAuditAgent:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.rpc_url))
        self.account = self.w3.eth.account.from_key(settings.private_key) if settings.private_key else None
        
        # Load contract ABI/address if deployed
        # For zero-friction demo, we simulate the on-chain anchor if contract is missing
        # But we still compute real SHA256 and Merkle roots
        self.audit_log = []
        self.contract = None
        self._load_contract()
        
    def _load_contract(self):
        try:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            artifact_path = os.path.join(root_dir, 'contracts', 'artifacts', 'contracts', 'EvidenceAnchor.sol', 'EvidenceAnchor.json')
            if os.path.exists(artifact_path):
                with open(artifact_path) as f:
                    artifact = json.load(f)
                
                # The address would normally be saved during deployment. 
                # For demo, we rely on the deploy script saving it.
                address_path = os.path.join(root_dir, 'contracts', 'deployed_address.txt')
                if os.path.exists(address_path):
                    with open(address_path) as f:
                        address = f.read().strip()
                    self.contract = self.w3.eth.contract(address=address, abi=artifact['abi'])
        except Exception as e:
            print(f"Contract not loaded: {e}")

    def compute_merkle_root(self, leaves):
        if not leaves:
            return hashlib.sha256(b"").hexdigest()
        
        current_layer = [hashlib.sha256(leaf.encode()).hexdigest() for leaf in leaves]
        
        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i+1] if i+1 < len(current_layer) else left
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                next_layer.append(combined)
            current_layer = next_layer
            
        return current_layer[0]

    async def log_query(self, operator_id, justification, query_text):
        if not justification:
            raise ValueError("Justification is required for audit logs.")
            
        prev_hash = self.audit_log[-1]["hash"] if self.audit_log else "0" * 64
        
        entry = {
            "timestamp": time.time(),
            "operator_id": operator_id,
            "justification": justification,
            "action": "QUERY",
            "query": query_text,
            "prev_hash": prev_hash
        }
        
        entry_str = json.dumps(entry, sort_keys=True)
        current_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry["hash"] = current_hash
        
        self.audit_log.append(entry)
        await bus.publish("AGENT_LOG", {"agent": "CryptoAudit", "msg": f"Audit logged query. Hash: {current_hash[:8]}..."})
        return current_hash

    async def anchor_timeline(self, case_id, trail):
        # 1. Canonicalize trail
        leaves = []
        for t in trail:
            # Only include immutable facts in the leaf
            leaf_dict = {
                "camera": t["camera_id"],
                "track": t["track_id"],
                "ts": t["timestamp"],
            }
            leaves.append(json.dumps(leaf_dict, sort_keys=True))
            
        merkle_root = self.compute_merkle_root(leaves)
        
        # 2. Canonical JSON of full evidence
        evidence_bundle = {
            "case_id": case_id,
            "merkle_root": merkle_root,
            "trail_length": len(trail),
            "timestamp": time.time()
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_bundle, sort_keys=True).encode()).hexdigest()
        
        # 3. Anchor on chain
        tx_hash = "simulated_tx_hash"
        block_number = 0
        if self.contract and self.account and self.w3.is_connected():
            try:
                tx = self.contract.functions.anchor(
                    "0x" + merkle_root,
                    "0x" + hashlib.sha256(case_id.encode()).hexdigest()
                ).build_transaction({
                    'from': self.account.address,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                    'gas': 2000000,
                    'gasPrice': self.w3.eth.gas_price
                })
                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=settings.private_key)
                tx_hash_bytes = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
                tx_hash = receipt.transactionHash.hex()
                block_number = receipt.blockNumber
                await bus.publish("AGENT_LOG", {"agent": "CryptoAudit", "msg": f"Anchored to blockchain. Tx: {tx_hash}"})
            except Exception as e:
                print(f"Blockchain tx failed: {e}")
        else:
             await bus.publish("AGENT_LOG", {"agent": "CryptoAudit", "msg": f"Simulated blockchain anchor. Root: {merkle_root[:8]}..."})
             
        return {
            "merkle_root": merkle_root,
            "evidence_hash": evidence_hash,
            "tx_hash": tx_hash,
            "block_number": block_number
        }
        
    def verify_chain(self):
        for i in range(1, len(self.audit_log)):
            prev = self.audit_log[i-1]
            curr = self.audit_log[i]
            if curr["prev_hash"] != prev["hash"]:
                return False
        return True

    def verify_evidence(self, merkle_root: str):
        if self.contract and self.w3.is_connected():
            try:
                # Ensure the merkle_root has '0x' prefix for bytes32
                if not merkle_root.startswith("0x"):
                    merkle_root = "0x" + merkle_root
                exists, timestamp, submitter = self.contract.functions.verify(merkle_root).call()
                return {
                    "exists": exists,
                    "timestamp": timestamp,
                    "submitter": submitter
                }
            except Exception as e:
                print(f"Blockchain verify failed: {e}")
                return {"exists": False, "error": str(e)}
        else:
             return {"exists": False, "error": "Not connected to blockchain or contract not loaded."}

crypto_agent = CryptoAuditAgent()
