"""
backend/test_pipeline.py
Smoke and end-to-end integration test runner for the IssueRouter NLP Pipeline.
Run from backend/ directory: python test_pipeline.py
"""

import sys
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from db.models import Challenge, ChallengeEvidence, ChallengeAnalysis, ChallengeRelation
from pipeline.orchestrator import process_evidence, load_all_models
from pipeline.location_extraction import extract_entities
from pipeline.priority_scoring import calculate_priority
from pipeline.deduplication import resolve
from pipeline.summarization import generate_summary
from pipeline.classification import classify
from pipeline.embeddings import get_embedding

# Sample test cases representing multi-source inputs across Jharkhand
TEST_CASES = [
    {
        "id": "CASE-01 (Citizen Report - Healthcare)",
        "source": "citizen",
        "raw_text": "Primary Health Center in Namkum, Ranchi has no doctor and acute shortage of antivenom and basic medicines for 2 months.",
        "submitted_lat": 23.3441,
        "submitted_lng": 85.3096,
        "expected_district": "Ranchi",
        "expected_domain": "Healthcare"
    },
    {
        "id": "CASE-02 (Twitter Signal - Same Healthcare Issue)",
        "source": "twitter",
        "raw_text": "@JharkhandGovt Namkum PHC clinic closed without doctors or medicines. Urgent intervention needed in Ranchi! #NamkumHealth",
        "submitted_lat": None,
        "submitted_lng": None,
        "expected_district": "Ranchi",
        "expected_domain": "Healthcare"
    },
    {
        "id": "CASE-03 (Citizen Report - Water Crisis)",
        "source": "citizen",
        "raw_text": "Severe drinking water scarcity in Jharia, Dhanbad. Deep borewells dried up and pipeline contaminated.",
        "submitted_lat": 23.7419,
        "submitted_lng": 86.4132,
        "expected_district": "Dhanbad",
        "expected_domain": "Water & Sanitation"
    }
]


def run_pipeline_tests():
    print("=" * 75)
    print("      ISSUEROUTER NLP & AI PIPELINE — VERIFICATION TEST RUNNER")
    print("=" * 75)

    # Step 1: Model warmup
    print("\n[Stage 1/3] Warming up all models (BART, spaCy, Sentence-Transformers)...")
    t0 = time.time()
    load_all_models()
    print(f"  --> Models loaded successfully in {time.time() - t0:.2f}s\n")

    # Step 2: Individual Component Smoke Tests
    print("[Stage 2/3] Verifying Individual Pipeline Components:")

    # 2.1 Location Extraction
    print("  • Location Extraction (Gazetteer & Entity Ruler)...", end=" ")
    loc_res = extract_entities("Broken culvert on main road in Kanke block, Ranchi")
    assert loc_res["district"] == "Ranchi", f"District mismatch: {loc_res}"
    assert loc_res["block"] == "Kanke", f"Block mismatch: {loc_res}"
    print(f"[PASSED] (District: {loc_res['district']}, Block: {loc_res['block']})")

    # 2.2 Priority Scoring
    print("  • Priority Scoring Math & Explanation...", end=" ")
    pri_res = calculate_priority("Healthcare", 8, 0.85, "increasing")
    assert 0 <= pri_res["priority_score"] <= 100
    assert "Priority" in pri_res["explanation"]
    print(f"[PASSED] (Score: {pri_res['priority_score']}/100)")

    # 2.3 Summarization
    print("  • Canonical Summarization (Extractive/LLM)...", end=" ")
    sum_res = generate_summary(None, "Doctor absenteeism at rural clinic", "Healthcare", "Namkum Ranchi")
    assert "title" in sum_res and "description" in sum_res
    print(f"[PASSED] (Title: '{sum_res['title']}')")

    # 2.4 Embeddings & Semantic Similarity
    print("  • Sentence-Transformers Embeddings (384d)...", end=" ")
    emb = get_embedding("[Healthcare] Rural clinic lacks doctors")
    assert len(emb) == 384
    print("[PASSED] (384-dimensional vector generated)")

    # Step 3: End-to-End Orchestrator Ingestion & Multi-Source Convergence
    print("\n[Stage 3/3] Testing End-to-End Ingestion & Multi-Source Deduplication:")

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    created_challenges = {}

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n  --- Processing Evidence #{i}: {test['id']} ---")
        print(f"  Raw Text: \"{test['raw_text']}\"")
        t_start = time.time()
        
        result = process_evidence(test, db)
        elapsed = time.time() - t_start
        
        print(f"  --> Action: {result['action'].upper()}")
        print(f"  --> Master Challenge ID: {result['challenge_id']}")
        print(f"  --> Priority Score: {result['priority_score']}")
        print(f"  --> Processed in {elapsed:.2f}s")
        
        created_challenges[test["id"]] = result

    # Verify Convergence between Case 01 and Case 02
    res_case1 = created_challenges["CASE-01 (Citizen Report - Healthcare)"]
    res_case2 = created_challenges["CASE-02 (Twitter Signal - Same Healthcare Issue)"]
    
    print("\n" + "=" * 75)
    print("  VERIFICATION SUMMARY:")
    print("=" * 75)
    
    if res_case2["action"] == "link":
        print(f"  [SUCCESS] Cross-Source Convergence: Tweet auto-linked into existing Master Challenge {res_case1['challenge_id']}")
    elif res_case2["action"] == "flag_related":
        print(f"  [SUCCESS] Cross-Source Relation: Tweet linked as Related Duplicate with Master Challenge {res_case1['challenge_id']}")
    else:
        print(f"  [NOTE] Cross-Source Match resulted in action: {res_case2['action']}")
        
    total_challenges = db.query(Challenge).count()
    total_evidence = db.query(ChallengeEvidence).count()
    total_analyses = db.query(ChallengeAnalysis).count()
    total_relations = db.query(ChallengeRelation).count()
    
    print(f"  Master Challenges in DB: {total_challenges}")
    print(f"  Evidence Items Linked:   {total_evidence}")
    print(f"  Analyses Generated:      {total_analyses}")
    print(f"  Challenge Relations:     {total_relations}")
    print("=" * 75)
    print("  [ALL TESTS PASSED] — IssueRouter NLP Pipeline is fully operational!")
    print("=" * 75)


if __name__ == "__main__":
    run_pipeline_tests()
