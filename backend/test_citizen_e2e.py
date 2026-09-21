"""
test_citizen_e2e.py — Comprehensive End-to-End Test for Citizen Experience & RBAC Security.
"""
import io
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from main import app
from pipeline.config import DOMAINS

def run_tests():
    print("=======================================================")
    print("      CITIZEN EXPERIENCE & RBAC VERIFICATION SUITE    ")
    print("=======================================================")

    client = TestClient(app)

    # ─────────────────────────────────────────────────────────────
    # TEST 1: Citizen Login & Profile
    # ─────────────────────────────────────────────────────────────
    print("\n[TEST 1] Citizen Login & Token Verification...")
    res = client.post("/api/auth/login", json={"email": "rahul@citizen.in", "password": "dummy"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    cit_data = res.json()
    assert cit_data["role"] == "Citizen", f"Expected Citizen role, got {cit_data['role']}"
    cit_token = cit_data["access_token"]
    cit_headers = {"Authorization": f"Bearer {cit_token}"}

    res_me = client.get("/api/auth/me", headers=cit_headers)
    assert res_me.status_code == 200, f"Get /me failed: {res_me.text}"
    me_data = res_me.json()
    assert me_data["name"] == "Rahul Kumar"
    assert me_data["role"] == "Citizen"
    print("[PASS] Citizen authenticated successfully. User:", me_data["name"])

    # ─────────────────────────────────────────────────────────────
    # TEST 2: Evidence Photo Upload & Static File Delivery
    # ─────────────────────────────────────────────────────────────
    print("\n[TEST 2] Photo Upload & Static File Serving...")
    fake_png = io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
    files = [("files", ("water_pipeline_leak.png", fake_png, "image/png"))]
    res_up = client.post("/api/challenges/upload-photos", files=files, headers=cit_headers)
    assert res_up.status_code == 200, f"Upload failed: {res_up.text}"
    saved_urls = res_up.json()
    assert len(saved_urls) == 1
    uploaded_photo_url = saved_urls[0]
    assert uploaded_photo_url.startswith("/uploads/evidence/")
    print("[PASS] Photo uploaded successfully:", uploaded_photo_url)

    res_static = client.get(uploaded_photo_url)
    assert res_static.status_code == 200, f"Static fetch failed: {res_static.status_code}"
    print("[PASS] Static delivery of uploaded evidence verified (HTTP 200).")

    # ─────────────────────────────────────────────────────────────
    # TEST 3: Challenge Creation & Ownership Tagging
    # ─────────────────────────────────────────────────────────────
    print("\n[TEST 3] Challenge Submission with Photo Evidence...")
    chal_payload = {
        "title": "Severe Arsenic Contamination in Kanke Handpumps",
        "description": "Residents in Kanke block have reported yellow water with hazardous chemical taste for over two weeks. Several cases of abdominal illness reported.",
        "location": "Near Panchayat Bhawan, Kanke, Ranchi, Jharkhand",
        "district": "Ranchi",
        "block": "Kanke",
        "lat": 23.4333,
        "lng": 85.3211,
        "media_urls": [uploaded_photo_url]
    }
    res_create = client.post("/api/challenges/", json=chal_payload, headers=cit_headers)
    assert res_create.status_code == 200, f"Challenge creation failed: {res_create.text}"
    created_chal = res_create.json()
    chal_id = created_chal["id"]
    assert created_chal["created_by"] == "user-cit-1"
    assert created_chal["domain"] in DOMAINS or len(created_chal["domain"]) > 0
    assert created_chal["status"] in ("pending_verification", "verified")
    assert uploaded_photo_url in (created_chal.get("media_urls") or [])
    print(f"[PASS] Challenge created: {chal_id} | Domain: {created_chal['domain']} | Owner: {created_chal['created_by']}")

    # ─────────────────────────────────────────────────────────────
    # TEST 4: Citizen My Progress Isolation
    # ─────────────────────────────────────────────────────────────
    print("\n[TEST 4] Citizen Progress Isolation (/api/challenges/my)...")
    res_my = client.get("/api/challenges/my", headers=cit_headers)
    assert res_my.status_code == 200, f"Fetch my challenges failed: {res_my.text}"
    my_challenges = res_my.json()
    my_chal_ids = [c["id"] for c in my_challenges]
    assert chal_id in my_chal_ids
    target_in_my = next(c for c in my_challenges if c["id"] == chal_id)
    assert uploaded_photo_url in (target_in_my.get("media_urls") or [])
    print(f"[PASS] Challenge {chal_id} verified in citizen's private progress list with photo attached.")

    # ─────────────────────────────────────────────────────────────
    # TEST 5: RBAC Route Enforcement (Citizen attempting Gov/Univ APIs)
    # ─────────────────────────────────────────────────────────────
    print("\n[TEST 5] RBAC Enforcement — Prohibiting Citizen from Admin APIs...")
    
    # 5.1 Verification attempt
    res_ver = client.patch(f"/api/challenges/{chal_id}/verify", json={"verified": True}, headers=cit_headers)
    assert res_ver.status_code == 403, f"Expected 403 Forbidden, got {res_ver.status_code}"
    print("[PASS] PATCH /api/challenges/{id}/verify blocked for Citizen (HTTP 403).")

    # 5.2 Routing attempt
    res_rt = client.post(f"/api/challenges/{chal_id}/route", json={"org_ids": ["org-univ-1"], "deadline": "2026-10-01T00:00:00"}, headers=cit_headers)
    assert res_rt.status_code == 403, f"Expected 403 Forbidden, got {res_rt.status_code}"
    print("[PASS] POST /api/challenges/{id}/route blocked for Citizen (HTTP 403).")

    # 5.3 Stats overview attempt
    res_st = client.get("/api/stats/overview", headers=cit_headers)
    assert res_st.status_code == 403, f"Expected 403 Forbidden, got {res_st.status_code}"
    print("[PASS] GET /api/stats/overview blocked for Citizen (HTTP 403).")

    # 5.4 University management attempt
    res_un = client.get("/api/universities/", headers=cit_headers)
    assert res_un.status_code == 403, f"Expected 403 Forbidden, got {res_un.status_code}"
    print("[PASS] GET /api/universities/ blocked for Citizen (HTTP 403).")

    # 5.5 University proposal submission attempt
    res_prop = client.post("/api/projects/proj-1/proposal", json={"solution_title": "hack", "proposed_solution": "hack", "budget_required": "1000"}, headers=cit_headers)
    assert res_prop.status_code == 403, f"Expected 403 Forbidden, got {res_prop.status_code}"
    print("[PASS] POST /api/projects/{id}/proposal blocked for Citizen (HTTP 403).")

    # 5.6 Unauthenticated request to protected endpoint
    res_unauth = client.get("/api/challenges/my")
    assert res_unauth.status_code == 401, f"Expected 401 Unauthorized, got {res_unauth.status_code}"
    print("[PASS] Unauthenticated GET /api/challenges/my blocked (HTTP 401).")

    # ─────────────────────────────────────────────────────────────
    # TEST 6: Government Verification & Evidence Continuity
    # ─────────────────────────────────────────────────────────────
    print("\n[TEST 6] Government Oversight & Evidence Continuity...")
    res_gov_login = client.post("/api/auth/login", json={"email": "gov@jharkhand.gov.in", "password": "dummy"})
    assert res_gov_login.status_code == 200
    gov_token = res_gov_login.json()["access_token"]
    gov_headers = {"Authorization": f"Bearer {gov_token}"}

    # Gov fetches the challenge
    res_gov_chal = client.get(f"/api/challenges/{chal_id}", headers=gov_headers)
    assert res_gov_chal.status_code == 200
    gov_chal_data = res_gov_chal.json()
    assert uploaded_photo_url in (gov_chal_data.get("media_urls") or []), "Citizen photo did not persist into Government view!"
    print("[PASS] Government user successfully views citizen challenge with matching photo evidence URL.")

    # Gov verifies the challenge
    res_gov_verify = client.patch(f"/api/challenges/{chal_id}/verify", json={"verified": True}, headers=gov_headers)
    assert res_gov_verify.status_code == 200
    assert res_gov_verify.json()["verified"] is True
    assert res_gov_verify.json()["status"] == "verified"
    print("[PASS] Government nodal officer successfully verified challenge.")

    # Gov accesses stats
    res_gov_stats = client.get("/api/stats/overview", headers=gov_headers)
    assert res_gov_stats.status_code == 200
    print("[PASS] Government stats overview accessible to authorized role.")

    print("\n=======================================================")
    print("        ALL TESTS PASSED! FULL SUITE 100% SUCCESS      ")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
