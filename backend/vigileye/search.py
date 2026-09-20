import numpy as np

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1, dtype=np.float32)
    vec2 = np.array(vec2, dtype=np.float32)
    dot = np.dot(vec1, vec2)
    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if norm == 0:
        return 0.0
    return float(dot / norm)

def search_embeddings(query_embedding, track_candidates, threshold=0.75):
    """
    Search for matches in track_candidates above threshold.
    track_candidates is a list of dicts with 'embedding' key.
    """
    results = []
    for track in track_candidates:
        sim = cosine_similarity(query_embedding, track["embedding"])
        if sim >= threshold:
            results.append({
                "track": track,
                "similarity": sim
            })
    # Sort by similarity descending
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results
