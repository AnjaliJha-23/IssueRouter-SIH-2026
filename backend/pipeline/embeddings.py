from sentence_transformers import SentenceTransformer

_embedder = None

def load_embedder():
    global _embedder
    if _embedder is None:
        print("[embeddings] Loading sentence-transformers model...")
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("[embeddings] Model loaded.")

def get_embedding(text: str) -> list[float]:
    """
    Returns a fixed-length embedding vector for the input text.
    """
    if _embedder is None:
        load_embedder()
        
    embedding = _embedder.encode(text)
    return embedding.tolist()
