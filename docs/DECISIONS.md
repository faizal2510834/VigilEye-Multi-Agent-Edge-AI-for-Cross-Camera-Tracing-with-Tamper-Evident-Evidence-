# Architecture Decision Record (ADR)

## 1. Predictive Handoff vs Continuous Inference
**Context**: Re-Identification (ReID) models like OSNet are compute-heavy. Running them 24/7 on 100 cameras requires massive edge infrastructure.
**Decision**: We implement "Predictive Handoff". Cameras only run lightweight detection (YOLOv8n). The Spatial Agent predicts when a target will arrive at the next camera based on transit priors, and only wakes up the heavy ReID model on that specific camera during that specific time window.
**Consequence**: Reduces compute usage significantly compared to continuous inference. 

*(Note: The TOPOLOGY transit-time values were tuned for the simulated single-video-split setup, which has near-zero transit between adjacent segments of one continuous recording, rather than measured real-camera distances. The demonstrated handoff match, e.g., cam_2_18 -> cam_3_18, is between adjacent segments of the same continuous walk, not an independent-camera re-identification.)*

## 2. Multi-Agent Bus vs Monolith
**Context**: Need to integrate spatial reasoning, LLMs, vision, and blockchain.
**Decision**: Asynchronous event bus (`backend/vigileye/agents/bus.py`). Agents subscribe to topics like `TRACE_REQUEST` and `EVIDENCE_READY`.
**Consequence**: Highly decoupled. Easy to swap the local Intent Parser for Azure OpenAI, or run Edge agents on physical Raspberry Pis.

## 3. Precomputed Artifacts for Demo
**Context**: 24-hour hackathon constraints.
**Decision**: Instead of requiring evaluators to download gigabytes of PyTorch weights and video, we ship precomputed `.onnx` models, extracted tracks, and JSON embeddings.
**Consequence**: Repo is lightweight. `make demo` runs instantly without a GPU.

## 4. Blockchain Anchoring
**Context**: Deepfakes make video evidence untrustworthy.
**Decision**: Build a Merkle tree of the timeline metadata and commit the root hash to an EVM smart contract.
**Consequence**: The chain of custody is mathematically provable. *(Note: `test_smoke.py` and `test_tamper.py` check key presence, return values, and stdout strings, not deep cryptographic correctness of the audit chain—this is honest scoping for the prototype.)*
