import subprocess
import os

def test_tamper_detection():
    # Run the verify_evidence script which has a built in tamper test
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    script_path = os.path.join(root_dir, 'scripts', 'verify_evidence.py')
    
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    
    assert "[PASS]" in result.stdout
    assert "[FAIL] Root mismatch!" in result.stdout
    print(result.stdout)
