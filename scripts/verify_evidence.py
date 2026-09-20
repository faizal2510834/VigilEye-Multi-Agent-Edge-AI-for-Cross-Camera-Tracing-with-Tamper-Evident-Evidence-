import hashlib
import json
import sys

def verify_merkle_root(leaves, expected_root):
    current_layer = [hashlib.sha256(leaf.encode()).hexdigest() for leaf in leaves]
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 2):
            left = current_layer[i]
            right = current_layer[i+1] if i+1 < len(current_layer) else left
            next_layer.append(hashlib.sha256((left + right).encode()).hexdigest())
        current_layer = next_layer
    
    computed_root = current_layer[0] if current_layer else hashlib.sha256(b"").hexdigest()
    if computed_root == expected_root:
        print(f"[PASS] Computed Merkle root matches expected: {expected_root}")
        return True
    else:
        print(f"[FAIL] Root mismatch!\nExpected: {expected_root}\nComputed: {computed_root}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_evidence.py <path_to_evidence_json>")
        sys.exit(1)
        
    path = sys.argv[1]
    import os
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
        
    with open(path, "r") as f:
        data = json.load(f)
        
    trail = data["trail"]
    expected_root = data["merkle_root"]
    
    leaves = [json.dumps({"camera": t["camera_id"], "track": t["track_id"], "ts": t["timestamp"]}, sort_keys=True) for t in trail]
    
    print("1. Valid verification:")
    if not verify_merkle_root(leaves, expected_root):
        print("Valid verification failed!")
        sys.exit(1)
        
    print("\n2. Tamper verification (modified timestamp):")
    if len(trail) > 0:
        tampered_trail = trail.copy()
        tampered_trail[0] = tampered_trail[0].copy()
        tampered_trail[0]["timestamp"] = tampered_trail[0].get("timestamp", 0) + 1.0
        t_leaves = [json.dumps({"camera": t["camera_id"], "track": t["track_id"], "ts": t["timestamp"]}, sort_keys=True) for t in tampered_trail]
        if verify_merkle_root(t_leaves, expected_root):
            print("Tamper verification incorrectly passed!")
            sys.exit(1)
            
if __name__ == "__main__":
    main()
