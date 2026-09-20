# VigilEye: Autonomous Multi-Agent AI & Edge Inference 👁️‍🗨️

**Verifiable, privacy-preserving person re-identification using predictive edge handoffs.**

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Next.js](https://img.shields.io/badge/Next.js-13+-black)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What it does
VigilEye is a multi-camera tracking system where four autonomous agents cooperate to track suspects. A user types a messy natural-language query ("guy in red shirt near main entrance"). The Intent Parsing agent translates this, and the Spatial Reasoning agent reconstructs the target's trail. Finally, the Cryptographic agent computes a tamper-evident hash chain and Merkle root, designed to anchor to an EVM blockchain (currently implemented against a local Hardhat RPC node).

## Why it's different: Predictive Handoffs
Instead of running compute-heavy ReID models on every camera 24/7, VigilEye uses **Predictive Handoffs**. 
When a target vanishes from Camera A, the Spatial Agent uses a learned topological graph to predict arrival times at adjacent cameras. **Only neighboring cameras wake up their heavy ReID models, and only during the expected arrival window.**

> **🔥 Measured Result: 16.1% reduction in edge compute usage, maintaining an 83% raw agreement rate (20/24 queries) vs continuous inference** 
>
> *(Qualitative Note: All 4 disagreements involved brute-force selecting a match with a physically impossible negative transit time, suggesting these queries have no true cross-camera partner in this dataset and brute-force was picking noise; handoff correctly did not return a match (or returned None) in these cases.)*
>
> *(Dataset Caveat: Measured on a small dataset, 12 track segments across 3 cameras).*

---

## Truth & Transparency: What is Real vs Simulated
*Hackathon constraint note: Building a full edge-hardware network with live video streams and live blockchain transactions in 24 hours is impossible. This is a prototype designed to prove the architecture.*

| Component | Status | Details |
| :--- | :--- | :--- |
| **Embeddings (Data)** | **Real (single-feed split, OpenCLIP+HSV)** | `data/cache` uses real features extracted from a pedestrian video, split to simulate multiple cameras. |
| **ONNX INT8 Models** | **Real (onnxruntime)** | `quantize.py` successfully converts YOLOv8 to INT8 and executes real tensor graphs for benchmarking. |
| **Smart Contracts** | **Real (local Hardhat, compiled/tested)** | The `EvidenceAnchor` contract compiles, deploys, and is fully tested against a real local Hardhat node in the `contracts/` directory. |
| **Crypto Agent / Web3** | **Real (local Hardhat RPC)** | Merkle root is computed and successfully anchored on-chain using web3.py interacting with the local Hardhat node. |
| **Static Demo Data** | **Precomputed** | `frontend/public/demo-data/*.json` files are populated directly from real benchmark/smoke output. |

---

## ⚡ 5-Minute Evaluation Guide (Static Demo)

No GPU? No API keys? No problem. We built a static fallback mode specifically for hackathon evaluators.

1. Clone the repo: `git clone https://github.com/your-org/vigileye.git && cd vigileye`
2. **Just run `make demo` (or launch the Next.js app natively with `cd frontend && npm install && npm run build && npm start`)**

*This will start a Next.js server locally, rendering the pre-computed static JSON responses for immediate evaluation.*

### Screenshots

* **Trace:** View the cross-camera timeline.
* **Agents:** Live WebSocket feed of the 4 autonomous agents.
* **Metrics:** The compute savings dashboard.
* **Evidence:** Blockchain tamper verification.

---

## 🏗️ Architecture

Read the full details in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/DECISIONS.md](docs/DECISIONS.md).

1. **Edge Perception Agents:** Quantized YOLOv8 + OpenCLIP + HSV running on camera nodes (INT8 quantization real; live edge deployment simulated via local process).
2. **Spatial Reasoning Agent:** Orchestrates predictive wake-ups and manages the adjacency graph.
3. **Intent Parsing Agent:** Converts NLP to JSON using regex (fallback) or Azure OpenAI. *(Limitation Note: Text queries currently pad HSV features with zeros, meaning they search purely on CLIP embeddings and cannot accurately match colors like "red shirt".)*
4. **Crypto Audit Agent:** Computes a Merkle root and hash chain; on-chain anchoring is executed via web3.py interacting with a local Hardhat node.

---

## 🛡️ Privacy & Security

Read our [Privacy Design (docs/PRIVACY.md)](docs/PRIVACY.md).
- Processing happens on the edge. Raw video never leaves the camera.
- Faces are automatically blurred.
- Immutable audit logs track every operator query.

---

## 🛠️ Commands (For Full Run)

If you want to run the full FastAPI backend + Hardhat network tests:

```bash
make setup       # Install pip and npm dependencies
make chain       # Start the local Hardhat node (run this in a separate terminal first!)
make deploy      # Deploy the Smart Contract to the local node
make backend     # Start the FastAPI backend via uvicorn (run this in a separate terminal!)
make smoke       # Run the backend pytest smoke test
make tamper-test # Demonstrate the cryptographic Merkle verification failing on altered data (Real Tamper Proof)
make benchmark   # Output the metrics comparing brute force vs handoffs
```

*(Note: The Evidence UI page features a "Simulate Tamper" button for demonstration purposes only. The true live cryptographic tamper detection is demonstrated by `make tamper-test` and `scripts/verify_evidence.py`.)*

---
*Built for ORION-PS-04: Autonomous Multi-Agent AI & Edge Inference Systems*
