import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pipeline.config import DEDUP_THRESHOLDS

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
    
    new_emb = np.array([new_embedding])
    
    best_match_id = None
    best_score = 0.0
    candidate_relations = []
    
    auto_link = DEDUP_THRESHOLDS["auto_link"]
    flag_related = DEDUP_THRESHOLDS["flag_related"]
    
    for cluster in filtered_candidates:
        canonical_emb = cluster.get("canonical_embedding")
        if not canonical_emb:
            continue
            
        centroid = np.array([canonical_emb])
        sim = float(cosine_similarity(new_emb, centroid)[0][0])
        
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