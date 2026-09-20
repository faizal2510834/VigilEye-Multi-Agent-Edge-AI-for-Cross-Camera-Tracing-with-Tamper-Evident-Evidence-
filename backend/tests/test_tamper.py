import subprocess
import os

def test_tamper_detection():
    # Run the verify_evidence script against the real evidence JSON
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    script_path = os.path.join(root_dir, 'scripts', 'verify_evidence.py')
    evidence_path = os.path.join(root_dir, 'data', 'evidence.json')
    
    if not os.path.exists(evidence_path):
        import pytest
        pytest.skip("evidence.json not found, run smoke test first")
        
    result = subprocess.run(["python", script_path, evidence_path], capture_output=True, text=True)
    
    print(result.stdout)
    assert "[PASS] Computed Merkle root matches expected" in result.stdout
    assert "[FAIL] Root mismatch!" in result.stdout
    assert result.returncode == 0
