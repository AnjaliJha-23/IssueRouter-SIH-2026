"""
backend/test_nlp_api_e2e.py
FastAPI TestClient verification of the NLP Pipeline API endpoints.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_nlp_api_integration():
    print("==========================================================")
    print("   TESTING FASTAPI NLP PIPELINE INTEGRATION ENDPOINTS    ")
    print("==========================================================")

    # 1. Health check
    res = client.get("/")
    assert res.status_code == 200
    print("[PASSED] [1/6] API Health check")

    # 2. List Challenges
    res = client.get("/api/challenges/")
    assert res.status_code == 200
    challenges = res.json()
    assert len(challenges) > 0
    print(f"[PASSED] [2/6] GET /api/challenges/ ({len(challenges)} challenges found)")

    # 3. Submit New Challenge via Citizen Form (Runs NLP Pipeline)
    print("  Submitting citizen issue to NLP pipeline...")
    citizen_payload = {
        "title": "Severe Hospital Supply Depletion",
        "description": "Primary Health Center in Namkum, Ranchi has acute shortage of life-saving medicines and antivenom for 2 months.",
        "location": "Namkum, Ranchi",
        "lat": 23.3441,
        "lng": 85.3096,
        "source": "citizen"
    }
    res = client.post("/api/challenges/", json=citizen_payload)
    assert res.status_code == 200, f"Error: {res.text}"
    created = res.json()
    cid = created["id"]
    print(f"[PASSED] [3/6] POST /api/challenges/ (Citizen Ingest)")
    print(f"         Created Challenge ID: {cid}")
    print(f"         Assigned Domain:      {created.get('domain')}")
    print(f"         Resolved Location:    {created.get('location')}")
    print(f"         Priority Score:       {created.get('priority_score')}/100")

    # 4. Ingest Raw Twitter Signal (Tests Deduplication / Multi-Source NLP)
    print("  Ingesting Twitter distress signal to NLP pipeline...")
    tweet_payload = {
        "source": "twitter",
        "raw_text": "@JharkhandGovt Urgent! Namkum PHC clinic closed without doctors or medicines in Ranchi. #NamkumHealth"
    }
    res = client.post("/api/challenges/ingest", json=tweet_payload)
    assert res.status_code == 200, f"Error: {res.text}"
    ingest_res = res.json()
    print(f"[PASSED] [4/6] POST /api/challenges/ingest")
    print(f"         Action:               {ingest_res.get('action')}")
    print(f"         Target Challenge ID:  {ingest_res.get('challenge_id')}")
    print(f"         Domain:               {ingest_res.get('domain')}")
    print(f"         Priority:             {ingest_res.get('priority_score')}")

    # 5. Fetch Evidence and AI Analysis
    res_ev = client.get(f"/api/challenges/{cid}/evidence")
    assert res_ev.status_code == 200
    evidences = res_ev.json()
    assert len(evidences) >= 1
    print(f"[PASSED] [5/6] GET /api/challenges/{cid}/evidence ({len(evidences)} evidence items)")

    res_an = client.get(f"/api/challenges/{cid}/analysis")
    assert res_an.status_code == 200
    analysis = res_an.json()
    assert analysis["domain"] is not None
    print(f"         GET /api/challenges/{cid}/analysis (Classifier: {analysis.get('model_versions', {}).get('classification')})")

    # 6. Trigger On-Demand AI Re-Analysis
    res_re = client.post(f"/api/challenges/{cid}/analyze")
    assert res_re.status_code == 200
    re_data = res_re.json()
    assert re_data["status"] == "success"
    print(f"[PASSED] [6/6] POST /api/challenges/{cid}/analyze (Re-calculated Priority: {re_data.get('priority_score')})")

    print("\n==========================================================")
    print("      ALL FASTAPI NLP INTEGRATION ENDPOINTS PASSED!       ")
    print("==========================================================")

if __name__ == "__main__":
    test_nlp_api_integration()
