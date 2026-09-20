# VigilEye Architecture

VigilEye uses a multi-agent microservices architecture optimized for edge inference and verifiable audit trails.

## Components

### 1. Edge Perception Agents (Edge)
- Lightweight autonomous agents running near the camera source.
- Uses INT8-quantized YOLOv8 and OSNet.
- Wakes up only when instructed by the Spatial Reasoning Agent.

### 2. Spatial Reasoning Agent (Core)
- Maintains the camera adjacency graph and temporal transit priors.
- Orchestrates **Predictive Handoff**: When a target disappears from `cam_1`, it calculates the probability distribution of arrival at `cam_2` and `cam_3` and instructs them to perform heavy ReID only during those specific time windows.

### 3. Intent Parsing Agent (Core)
- Parses messy natural language ("guy in red shirt near the entrance") into structured metadata.
- Rule-based regex fallback + Azure OpenAI integration.

### 4. Cryptographic Audit Agent (Core)
- Builds a Merkle tree of the timeline evidence.
- Anchors the Merkle root to a smart contract (`EvidenceAnchor.sol`) on an EVM-compatible blockchain.

## Data Flow
1. User submits query to `FastAPI` backend.
2. `Intent Parsing` structures the query.
3. `Spatial Reasoning` starts the trace at the first camera, waking up `Edge` agents predictively.
4. The trace completes and is handed to `Crypto Audit`.
5. The timeline is hashed, anchored, and returned to the Next.js frontend via REST and WebSockets.
