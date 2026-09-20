# Privacy by Design

VigilEye prioritizes citizen privacy while maintaining security capabilities.

## 1. On-Edge Processing
Raw video never leaves the camera node. `Edge Perception Agents` process frames locally, extracting abstract numerical embeddings (vectors of 512 floats) and throwing away the video stream. Only these embeddings are sent to the central `Spatial Reasoning Agent`.

## 2. Automated Face Blurring
If raw crops are required for human verification (e.g., presenting evidence in court), the `prepare_data.py` pipeline applies OpenCV Gaussian blur to detected faces *before* the crops are stored or transmitted.

## 3. Ephemeral Storage
Embeddings and traces are stored ephemerally. Once a trace is verified and its hash is anchored to the blockchain, the central system discards the intermediate tracking data.

## 4. Tamper-Evident Audit Trail
The `Crypto Audit Agent` logs every query made by an operator. This means surveillance cannot happen in secret; there is an immutable record of *who* searched for *what*, and *when*.
