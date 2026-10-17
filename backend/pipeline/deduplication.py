import numpy as np

from pipeline.config import DEDUP_THRESHOLDS


def _unit_vector(vector) -> np.ndarray | None:
    """
    L2-normalise a vector, or return None when it cannot be compared.

    Returning None (rather than raising) keeps malformed or missing vectors
    from turning into a failed citizen submission.
    """
    if vector is None:
        return None
    try:
        arr = np.asarray(vector, dtype=np.float64).ravel()
    except (TypeError, ValueError):
        return None
    if arr.size == 0 or not np.all(np.isfinite(arr)):
        return None
    norm = float(np.linalg.norm(arr))
    if norm == 0.0:
        return None
    return arr / norm


def resolve(
    new_embedding: list[float],
    new_domain: str,
    new_district: str,
    candidate_challenges: list[dict]
) -> dict:
    """
    Resolves a new evidence embedding against existing candidate Master Challenges.
    
    candidate_challenges: list of dicts with keys:
        - id: str
        - domain: str
        - district: str
        - canonical_embedding: list[float]
        
    Returns dict:
        {
            "action": "link" | "flag_related" | "new_challenge",
            "matched_challenge_id": "HC-102" | None,
            "similarity_score": 0.84,
            "candidate_relations": [{"challenge_id": "HC-098", "score": 0.71}]
        }
    """
    # Filter candidates by same domain and district to reduce search space
    filtered_candidates = [
        c for c in candidate_challenges 
        if c.get("domain") == new_domain and c.get("district") == new_district
    ]
    
    if not filtered_candidates:
        return {
            "action": "new_challenge",
            "matched_challenge_id": None,
            "similarity_score": 0.0,
            "candidate_relations": []
        }
    
    new_emb = _unit_vector(new_embedding)
    if new_emb is None:
        # No usable vector for the incoming evidence, so dedup cannot run.
        return {
            "action": "new_challenge",
            "matched_challenge_id": None,
            "similarity_score": 0.0,
            "candidate_relations": []
        }
    
    best_match_id = None
    best_score = 0.0
    candidate_relations = []
    
    auto_link = DEDUP_THRESHOLDS["auto_link"]
    flag_related = DEDUP_THRESHOLDS["flag_related"]
    
    for cluster in filtered_candidates:
        centroid = _unit_vector(cluster.get("canonical_embedding"))
        if centroid is None:
            continue
        if centroid.shape != new_emb.shape:
            # Produced by a different embedding model or dimension: the two
            # vectors live in unrelated spaces, so a score would be noise.
            # Skip instead of crashing on a shape mismatch.
            continue
        
        # Both vectors are unit length, so the dot product is the cosine.
        sim = float(np.dot(new_emb, centroid))
        
        if sim > best_score:
            best_score = sim
            best_match_id = cluster["id"]
            
        if flag_related <= sim < auto_link:
            candidate_relations.append({"challenge_id": cluster["id"], "score": round(sim, 3)})
            
    # Sort relations by score descending
    candidate_relations.sort(key=lambda x: x["score"], reverse=True)
    
    if best_score >= auto_link:
        return {
            "action": "link",
            "matched_challenge_id": best_match_id,
            "similarity_score": round(best_score, 3),
            "candidate_relations": []
        }
    elif best_score >= flag_related:
        return {
            "action": "flag_related",
            "matched_challenge_id": None,
            "similarity_score": round(best_score, 3),
            "candidate_relations": candidate_relations
        }
    else:
        return {
            "action": "new_challenge",
            "matched_challenge_id": None,
            "similarity_score": round(best_score, 3),
            "candidate_relations": []
        }
