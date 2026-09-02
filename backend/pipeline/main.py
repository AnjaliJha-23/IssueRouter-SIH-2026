"""
Main pipeline orchestrator.
Takes a raw tweet dict → returns a fully processed PostResult dict.
This is the only function the ingestion service calls.
"""
from pipeline.classifier import classify, load_classifier
from pipeline.ner import extract_entities, load_ner
from pipeline.urgency import score_urgency, get_urgency_weight
from pipeline.router import route_department
from pipeline.clusterer import get_embedding, load_clusterer
from ingestion.normaliser import clean_text

def load_all_models():
    """Call this at FastAPI startup to warm all models before first request."""
    print("[pipeline] Warming up all models...")
    load_classifier()
    load_ner()
    load_clusterer()
    print("[pipeline] All models ready.")

def process_post(raw_tweet: dict) -> dict:
    """
    Input:
        raw_tweet = {
            "id": str,
            "username": str,
            "text": str,
            "likes": int,
            "retweets": int,
            "created_at": str
        }

    Output:
        {
            "tweet_id": str,
            "username": str,
            "raw_text": str,
            "clean_text": str,
            "category": str,
            "confidence": float,
            "location": str | None,
            "department_mentioned": str | None,
            "urgency": str,
            "urgency_weight": int,
            "department": str,
            "embedding": list[float],
            "likes": int,
            "retweets": int,
        }
    """
    raw_text = raw_tweet.get("text", "")
    retweets = raw_tweet.get("retweets", 0)

    # Step 1: Clean
    text = clean_text(raw_text)

    # Step 2: Classify
    category, confidence = classify(text)

    # Step 3: NER
    entities = extract_entities(text)
    location = entities.get("location")
    department_mentioned = entities.get("department_mentioned")

    # Step 4: Urgency
    urgency = score_urgency(text, retweets)
    urgency_weight = get_urgency_weight(urgency)

    # Step 5: Route
    department = route_department(category, location or "")

    # Step 6: Embed (for clustering)
    embedding = get_embedding(text)

    return {
        "tweet_id":            raw_tweet.get("id"),
        "username":            raw_tweet.get("username"),
        "raw_text":            raw_text,
        "clean_text":          text,
        "category":            category,
        "confidence":          confidence,
        "location":            location,
        "department_mentioned": department_mentioned,
        "urgency":             urgency,
        "urgency_weight":      urgency_weight,
        "department":          department,
        "embedding":           embedding,
        "likes":               raw_tweet.get("likes", 0),
        "retweets":            retweets,
    }