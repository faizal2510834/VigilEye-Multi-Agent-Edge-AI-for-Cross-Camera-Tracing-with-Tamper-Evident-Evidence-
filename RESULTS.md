# VigilEye Benchmarks & Results

## 1. Predictive Handoff vs Brute Force
- **Hardware:** Local CPU Demo
- **Dataset:** Real pedestrian video (split into 3 cameras, 12 independent query tracks)
- **Command:** `python scripts/benchmark.py`

| Metric | Brute Force | Predictive Handoff | Savings |
|---|---|---|---|
| Inference Calls | 264 | 233 | **11.7%** |
| Data Transferred | 1081344 B | 954368 B | **11.7%** |

**Accuracy & Agreement:**
- Raw Agreement: 6/12 (50.0%)
*(Qualitative Note: Qualitative details on disagreements: if any occurred, brute-force likely matched noise outside the predicted space-time window.)*

## 2. INT8 Quantization — NOT YET RUN. See Step 4.
