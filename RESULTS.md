# VigilEye Benchmarks & Results

## 1. Predictive Handoff vs Brute Force
- **Hardware:** Local CPU Demo
- **Dataset:** Real pedestrian video (split into 3 cameras, 12 independent query tracks)
- **Command:** `python scripts/benchmark.py`

| Metric | Brute Force | Predictive Handoff | Savings |
|---|---|---|---|
| Inference Calls | 264 | 154 | **41.7%** |
| Data Transferred | 1081344 B | 630784 B | **41.7%** |

**Accuracy & Agreement:**
- Raw Agreement: 9/12 (75.0%)
*(Qualitative Note: All 3 disagreements involved brute-force selecting a match with a physically impossible negative transit time (matching noise outside the possible space-time window), which handoff correctly ignored.)*

## 2. INT8 Quantization — NOT YET RUN. See Step 4.
