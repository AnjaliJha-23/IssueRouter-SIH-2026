import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_model = None
SIMILARITY_THRESHOLD = 0.82  # tune this if clusters are too big or too small

def load_clusterer():
    global _model
    if _model is None:
        print("[clusterer] Loading sentence-transformers model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[clusterer] Model loaded.")

def get_embedding(text: str) -> list:
    if _model is None:
        load_clusterer()
    return _model.encode(text).tolist()

def find_matching_cluster(
    new_text: str,
    new_category: str,
    existing_clusters: list
) -> str | None:
    """
    Compares new tweet embedding against existing cluster centroids.
    Returns cluster_id if match found, None if new cluster should be created.

    existing_clusters: list of dicts with keys:
        id, category, centroid_embedding (list of floats)
    """
    if _model is None:
        load_clusterer()

    if not existing_clusters:
        return None

    new_emb = _model.encode(new_text)

    for cluster in existing_clusters:
        # Only compare same category — don't mix infrastructure with sanitation
        if cluster["category"] != new_category:
            continue

        centroid = np.array(cluster["centroid_embedding"])
        sim = cosine_similarity([new_emb], [centroid])[0][0]

        if sim >= SIMILARITY_THRESHOLD:
            return cluster["id"]

    return None

def update_centroid(
    old_centroid: list,
    new_text: str,
    complaint_count: int
) -> list:
    """
    Incrementally updates cluster centroid with new tweet embedding.
    Uses running average formula.
    """
    if _model is None:
        load_clusterer()

    old = np.array(old_centroid)
    new_emb = _model.encode(new_text)

    # Running average: new_centroid = (old * (n-1) + new) / n
    updated = (old * (complaint_count - 1) + new_emb) / complaint_count
    return updated.tolist()