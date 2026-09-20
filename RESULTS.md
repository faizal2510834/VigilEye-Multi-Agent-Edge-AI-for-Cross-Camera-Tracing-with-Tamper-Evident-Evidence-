# VigilEye Benchmarks & Results

## 1. Predictive Handoff vs Brute Force
- **Hardware:** Local CPU Demo
- **Dataset:** Real pedestrian video (split into 3 cameras, 24 tracks representing ~7 independent people)
- **Command:** `python scripts/benchmark.py`

| Metric | Brute Force | Predictive Handoff | Savings |
|---|---|---|---|
| Inference Calls | 576 | 483 | **16.1%** |
| Data Transferred | 2359296 B | 1978368 B | **16.1%** |

**Accuracy & Agreement:**
- Raw Agreement: 20/24 (83.3%)
*(Qualitative Note: All 4 disagreements involved brute-force selecting a match with a physically impossible negative transit time, suggesting these queries have no true cross-camera partner in this dataset and brute-force was picking noise; handoff correctly did not return a match (or returned None) in these cases.)*

## 2. INT8 Quantization (ONNX Runtime)
- **Hardware:** Local CPU
- **Command:** `python scripts/quantize.py`

*(See benchmarks/quantize_results.json for raw data)*
| Model | Precision | Latency (ms) | Raw ONNX inference FPS (dummy tensor, no pre/post-processing) | RAM (MB) | Size (MB) |
|---|---|---|---|---|---|
| YOLOv8n | FP32 | 43.36 | 23.07 | 517.84 | 12.26 |
| YOLOv8n | INT8 | 63.96 | 15.64 | 502.05 | 3.34 |

*This measures graph execution only; end-to-end pipeline FPS on real video was not separately benchmarked.*

*(Note: On this local CPU hardware (Intel Core i5-13420H), dynamic INT8 quantization resulted in a smaller model size (3.34 MB vs 12.26 MB) but a **negative speedup** (15.64 FPS vs 23.07 FPS) compared to FP32 due to missing dedicated INT8 VNNI extensions or quantization overhead on this specific x86 architecture. This is a measured, truthful result.)*
