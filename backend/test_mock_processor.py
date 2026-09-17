"""
backend/test_mock_processor.py

Custom JSON Test Mechanism for IssueRouter NLP Pipeline.
Processes any mock JSON input through the full NLP Pipeline and outputs
the exact frontend-ready JSON payload that the dashboard consumes.

Usage:
  1. Default Test Run (uses sample JSON):
     python test_mock_processor.py

  2. Pass a custom JSON file:
     python test_mock_processor.py --file path/to/your_mock.json

  3. Save the frontend-ready output JSON to a file:
     python test_mock_processor.py --output frontend_mock_output.json
"""
import sys
import os

# Ensure backend root is in sys.path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import json
import argparse
import time
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from db.models import Challenge, ChallengeEvidence, ChallengeAnalysis, ChallengeRelation
from pipeline.orchestrator import process_evidence, load_all_models

# Sample mock JSON template that users can provide
DEFAULT_MOCK_INPUT = {
    "source": "citizen",
    "raw_text": "Primary Health Center in Namkum, Ranchi has no doctor on duty and acute shortage of antivenom and emergency medicines for 2 months.",
    "submitted_lat": 23.3441,
    "submitted_lng": 85.3096,
    "author": "Citizen Citizen_Ranchi_01",
    "metadata": {
        "channel": "web_form",
        "district_hint": "Ranchi"
    }
}


def create_in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def process_mock_json(input_json: dict, db_session=None) -> dict:
    """
    Takes arbitrary mock input JSON, passes it through the AI/NLP Pipeline,
    and structures the output into the complete Frontend-Ready schema.
    """
    if db_session is None:
        db_session = create_in_memory_db()

    start_time = time.time()
    
    # 1. Execute through Orchestrator
    pipeline_res = process_evidence(input_json, db_session)
    challenge_id = pipeline_res["challenge_id"]
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    # 2. Fetch the newly created / updated records from DB
    challenge = db_session.query(Challenge).filter(Challenge.id == challenge_id).first()
    analysis = db_session.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == challenge_id).first()
    evidences = db_session.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == challenge_id).all()
    relations = db_session.query(ChallengeRelation).filter(ChallengeRelation.source_challenge_id == challenge_id).all()

    # 3. Construct the comprehensive Frontend Dashboard Payload
    frontend_payload = {
        "_meta": {
            "processing_time_ms": elapsed_ms,
            "pipeline_action": pipeline_res["action"],
            "processed_at": datetime.utcnow().isoformat() + "Z"
        },
        # Structure matching Frontend Challenge Card / Detail View
        "challenge": {
            "id": challenge.id,
            "title": challenge.title,
            "description": challenge.ai_generated_summary or challenge.official_description or input_json.get("raw_text", ""),
            "domain": challenge.domain,
            "subdomain": analysis.subdomain if analysis else None,
            "status": challenge.status or "pending_verification",
            "priority_score": challenge.priority_score,
            "location": challenge.location or f"{challenge.block or ''}, {challenge.district or ''}".strip(),
            "district": challenge.district,
            "block": challenge.block,
            "lat": challenge.lat or input_json.get("submitted_lat"),
            "lng": challenge.lng or input_json.get("submitted_lng"),
            "verified": bool(challenge.verified),
            "complaint_count": len(evidences),
            "trend": analysis.trend if analysis else "stable",
            "created_at": challenge.created_at.isoformat() if hasattr(challenge, "created_at") and challenge.created_at else datetime.utcnow().isoformat()
        },
        # AI Explainability & Breakdown (for Gov / Admin Inspection panel)
        "ai_analysis": {
            "domain_classification": {
                "top_domain": analysis.domain if analysis else challenge.domain,
                "subdomain": analysis.subdomain if analysis else None,
                "domain_scores": analysis.domain_scores if analysis else {}
            },
            "priority_breakdown": {
                "score": analysis.priority_score if analysis else challenge.priority_score,
                "factors": analysis.priority_factors if analysis else {},
                "explanation": analysis.explanation if analysis else "Calculated based on domain severity and multi-source corroboration."
            },
            "deduplication": {
                "action_taken": pipeline_res["action"],
                "matched_challenge_id": pipeline_res.get("matched_challenge_id"),
                "related_challenges": [
                    {
                        "target_id": r.target_challenge_id,
                        "similarity_score": r.similarity_score
                    } for r in relations
                ]
            }
        },
        # Evidence items linked to this challenge (for Evidence Timeline tab)
        "evidences": [
            {
                "id": ev.id,
                "source": ev.source,
                "clean_text": ev.clean_text,
                "raw_text": ev.raw_text,
                "submitted_lat": ev.submitted_lat,
                "submitted_lng": ev.submitted_lng,
                "created_at": ev.created_at.isoformat() if hasattr(ev, "created_at") and ev.created_at else datetime.utcnow().isoformat()
            } for ev in evidences
        ]
    }

    return frontend_payload


def main():
    parser = argparse.ArgumentParser(description="Test NLP Pipeline with Mock JSON")
    parser.add_argument("--file", type=str, help="Path to custom input mock JSON file")
    parser.add_argument("--output", type=str, help="Path to write the processed output JSON file")
    args = parser.parse_args()

    input_data = DEFAULT_MOCK_INPUT
    if args.file:
        if not os.path.exists(args.file):
            print(f"[Error] File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            input_data = json.load(f)

    print("=" * 80)
    print("        ISSUEROUTER NLP PIPELINE — MOCK JSON PROCESSOR TEST HARNESS")
    print("=" * 80)
    print("\n[Input Mock JSON received]:")
    print(json.dumps(input_data, indent=2))

    print("\n[Processing through NLP Pipeline (Normalization -> Classification -> NER -> Embedding -> Dedup -> Scoring)]...")
    
    db = create_in_memory_db()
    result = process_mock_json(input_data, db)

    print("\n" + "=" * 80)
    print("        PROCESSED FRONTEND-READY JSON PAYLOAD (FOR DASHBOARD)")
    print("=" * 80)
    formatted_output = json.dumps(result, indent=2)
    print(formatted_output)

    output_path = args.output or "frontend_mock_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_output)
    print(f"\n[Success] Output JSON successfully saved to: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
