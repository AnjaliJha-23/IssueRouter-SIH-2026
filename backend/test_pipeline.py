"""
Quick smoke test for the full AI pipeline.
Run from backend/ dir:  python test_pipeline.py
"""
import os, sys, json, time
from dotenv import load_dotenv

load_dotenv()   # load .env so GROQ_API_KEY is available

from pipeline.main import process_post, load_all_models

# ── Sample tweets to test ──────────────────────────────────────
TEST_TWEETS = [
    {
        "id": "test_001",
        "username": "angry_citizen",
        "text": "@DelhiGovt Massive pothole on Mayur Vihar main road! 3 accidents this week. Fix ASAP! #complaints_gov https://t.co/abc123",
        "likes": 45,
        "retweets": 120,
        "created_at": "2026-04-19T10:00:00Z"
    },
    {
        "id": "test_002",
        "username": "mumbai_resident",
        "text": "No water supply in Andheri for 2 days! MCGM please respond. We are suffering! #complaints_gov",
        "likes": 200,
        "retweets": 510,
        "created_at": "2026-04-19T11:30:00Z"
    },
    {
        "id": "test_003",
        "username": "bangalorean",
        "text": "Garbage piling up in Koramangala near the park. Stinking badly. BBMP do something #complaints_gov",
        "likes": 12,
        "retweets": 5,
        "created_at": "2026-04-19T12:00:00Z"
    },
]


def run_test():
    print("=" * 70)
    print("  ISSUE ROUTER — PIPELINE SMOKE TEST")
    print("=" * 70)

    # Step 1: Load all models
    print("\n[1/2] Loading all models (first run downloads them)...\n")
    start = time.time()
    load_all_models()
    print(f"\n[OK] Models loaded in {time.time() - start:.1f}s\n")

    # Step 2: Process each test tweet
    print("[2/2] Processing test tweets...\n")

    for i, tweet in enumerate(TEST_TWEETS, 1):
        print(f"{'-' * 70}")
        print(f"  TWEET #{i}: @{tweet['username']}")
        print(f"  Raw: {tweet['text'][:80]}...")
        print(f"{'-' * 70}")

        start = time.time()
        result = process_post(tweet)
        elapsed = time.time() - start

        print(f"  Clean text:   {result['clean_text']}")
        print(f"  Category:     {result['category']} ({result['confidence']})")
        print(f"  Location:     {result['location'] or '(none detected)'}")
        print(f"  Department:   {result['department']}")
        print(f"  Urgency:      {result['urgency']} (weight: {result['urgency_weight']})")
        print(f"  Dept mention: {result['department_mentioned'] or '(none)'}")
        print(f"  Embedding:    [{len(result['embedding'])} dims]")
        print(f"  >> Processed in {elapsed:.2f}s")
        print()

    print("=" * 70)
    print("  [OK] ALL TESTS PASSED - Pipeline is working!")
    print("=" * 70)


if __name__ == "__main__":
    run_test()
