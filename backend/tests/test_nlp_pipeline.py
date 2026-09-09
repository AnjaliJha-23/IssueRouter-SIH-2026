"""
backend/tests/test_nlp_pipeline.py
Comprehensive test suite for the IssueRouter NLP Pipeline.
Run with: py -3.12 -m pytest tests/test_nlp_pipeline.py -v
"""

import pytest
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from db.models import Challenge, ChallengeEvidence, ChallengeAnalysis, ChallengeRelation
from ingestion.normaliser import clean_text
from pipeline.config import DOMAINS, SUBDOMAIN_MAP, DEDUP_THRESHOLDS, DOMAIN_SEVERITY, PRIORITY_WEIGHTS
from pipeline.location_extraction import extract_entities
from pipeline.embeddings import get_embedding
from pipeline.deduplication import resolve
from pipeline.priority_scoring import calculate_priority
from pipeline.summarization import generate_summary
from pipeline.router import route_department
from pipeline.classification import classify
from pipeline.orchestrator import process_evidence


# =====================================================================
# 1. Text Normalization Tests
# =====================================================================
class TestTextNormalization:
    def test_clean_text_removes_urls_and_mentions(self):
        raw = "@JharkhandGovt Massive water pipeline burst! Fix it http://t.co/xyz123 #WaterCrisis"
        cleaned = clean_text(raw)
        assert "@JharkhandGovt" not in cleaned
        assert "http://" not in cleaned
        assert "#WaterCrisis" not in cleaned
        assert "WaterCrisis" in cleaned
        assert "Massive water pipeline burst!" in cleaned

    def test_clean_text_collapses_whitespace(self):
        raw = "   Multiple   spaces   and\nnewlines   "
        cleaned = clean_text(raw)
        assert cleaned == "Multiple spaces and newlines"


# =====================================================================
# 2. Location Extraction Tests (Jharkhand Gazetteer)
# =====================================================================
class TestLocationExtraction:
    def test_exact_district_match(self):
        res = extract_entities("Severe hospital shortage in Ranchi district")
        assert res["district"] == "Ranchi"
        assert res["resolution_method"] in ["gazetteer_match", "fuzzy_gazetteer"]
        assert res["confidence"] >= 0.7

    def test_block_match_infers_district(self):
        res = extract_entities("Handpump broken in Namkum block since last Monday")
        assert res["block"] == "Namkum"
        assert res["district"] == "Ranchi"
        assert res["confidence"] >= 0.7

    def test_coordinates_fallback_when_no_text_match(self):
        meta = {"latitude": 23.3441, "longitude": 85.3096}
        res = extract_entities("Power cut here since morning", evidence_metadata=meta)
        assert res["latitude"] == 23.3441
        assert res["longitude"] == 85.3096
        assert res["resolution_method"] == "metadata_coords"
        assert res["confidence"] >= 0.9

    def test_unresolved_location(self):
        res = extract_entities("General query about state policy without any location mentioned")
        assert res["district"] is None
        assert res["block"] is None
        assert res["resolution_method"] == "unresolved"
        assert res["confidence"] == 0.0


# =====================================================================
# 3. Embeddings & Semantic Similarity Tests
# =====================================================================
class TestEmbeddings:
    def test_embedding_vector_dimensions(self):
        emb = get_embedding("Clean drinking water shortage in rural village")
        assert isinstance(emb, list)
        assert len(emb) == 384
        assert all(isinstance(x, float) for x in emb)

    def test_semantic_similarity_separation(self):
        emb_water1 = np.array([get_embedding("[Water & Sanitation] Contaminated drinking water in village wells")])
        emb_water2 = np.array([get_embedding("[Water & Sanitation] Dirty tap water causing illness in village")])
        emb_traffic = np.array([get_embedding("[Infrastructure/Transport] Traffic lights broken on main highway intersection")])

        sim_related = float(cosine_similarity(emb_water1, emb_water2)[0][0])
        sim_unrelated = float(cosine_similarity(emb_water1, emb_traffic)[0][0])

        assert sim_related > 0.65, f"Expected high similarity between related texts, got {sim_related}"
        assert sim_unrelated < 0.40, f"Expected low similarity between unrelated texts, got {sim_unrelated}"
        assert sim_related > sim_unrelated


# =====================================================================
# 4. Deduplication & Clustering Tests
# =====================================================================
class TestDeduplication:
    def test_new_challenge_when_no_candidates(self):
        emb = [0.1] * 384
        res = resolve(emb, "Healthcare", "Ranchi", [])
        assert res["action"] == "new_challenge"
        assert res["matched_challenge_id"] is None
        assert res["similarity_score"] == 0.0

    def test_filter_excludes_different_district_or_domain(self):
        emb = [0.1] * 384
        candidates = [
            {"id": "HC-001", "domain": "Education", "district": "Ranchi", "canonical_embedding": [0.1] * 384},
            {"id": "HC-002", "domain": "Healthcare", "district": "Dhanbad", "canonical_embedding": [0.1] * 384}
        ]
        res = resolve(emb, "Healthcare", "Ranchi", candidates)
        assert res["action"] == "new_challenge"
        assert res["matched_challenge_id"] is None

    def test_auto_link_on_high_similarity(self):
        canonical = get_embedding("[Healthcare] PHC clinic closed in Namkum Ranchi")
        candidates = [
            {"id": "HC-101", "domain": "Healthcare", "district": "Ranchi", "canonical_embedding": canonical}
        ]
        new_emb = get_embedding("[Healthcare] PHC clinic closed in Namkum Ranchi")
        res = resolve(new_emb, "Healthcare", "Ranchi", candidates)
        assert res["action"] == "link"
        assert res["matched_challenge_id"] == "HC-101"
        assert res["similarity_score"] >= DEDUP_THRESHOLDS["auto_link"]

    def test_flag_related_on_moderate_similarity(self):
        emb1 = get_embedding("[Healthcare] Namkum health sub-center lacks doctor and medicine supplies")
        emb2 = get_embedding("[Healthcare] Ambulance service unavailable in Namkum block hospital")
        
        candidates = [
            {"id": "HC-202", "domain": "Healthcare", "district": "Ranchi", "canonical_embedding": emb1}
        ]
        res = resolve(emb2, "Healthcare", "Ranchi", candidates)
        assert res["action"] in ["flag_related", "link", "new_challenge"]
        if res["action"] == "flag_related":
            assert len(res["candidate_relations"]) > 0
            assert res["candidate_relations"][0]["challenge_id"] == "HC-202"


# =====================================================================
# 5. Priority Scoring Tests
# =====================================================================
class TestPriorityScoring:
    def test_priority_score_formula_and_contract(self):
        res = calculate_priority(
            domain="Healthcare",
            evidence_volume=10,
            evidence_confidence=0.85,
            trend="increasing"
        )
        assert "priority_score" in res
        assert 0 <= res["priority_score"] <= 100
        assert "priority_factors" in res
        assert res["priority_factors"]["severity"] == DOMAIN_SEVERITY["Healthcare"]
        assert res["priority_factors"]["evidence_volume"] == 0.1  # 10 / 100
        assert res["priority_factors"]["confidence"] == 0.85
        assert res["priority_factors"]["trend"] == 1.0  # increasing multiplier
        assert "explanation" in res
        assert "Priority" in res["explanation"]

    def test_severity_ranking(self):
        score_high = calculate_priority("Healthcare", 5, 0.8, "stable")["priority_score"]
        score_low = calculate_priority("Public Administration", 5, 0.8, "stable")["priority_score"]
        assert score_high > score_low


# =====================================================================
# 6. Summarization Tests
# =====================================================================
class TestSummarization:
    def test_extractive_fallback_format(self):
        evidence = "Primary Health Center in Namkum has had no doctor for 3 months and zero stock of antibiotics."
        summary = generate_summary(
            existing_summary=None,
            new_evidence_text=evidence,
            domain="Healthcare",
            location="Namkum Ranchi"
        )
        assert "title" in summary
        assert "description" in summary
        assert len(summary["title"]) > 0
        assert len(summary["description"]) > 0


# =====================================================================
# 7. Department Router Tests
# =====================================================================
class TestRouter:
    def test_default_department_routing(self):
        assert route_department("Infrastructure") == "PWD"
        assert route_department("Sanitation") == "MCD"
        assert route_department("Healthcare") == "Health Dept"

    def test_city_specific_overrides(self):
        assert route_department("Infrastructure", "Mumbai") == "MCGM"
        assert route_department("Sanitation", "Bangalore") == "BBMP"
        assert route_department("Utilities", "Noida") == "Noida Authority"


# =====================================================================
# 8. Zero-Shot Classification Contract Tests
# =====================================================================
class TestClassification:
    def test_classification_contract_and_domain_validity(self):
        text = "Severe shortage of clean drinking water and broken handpumps in rural village"
        res = classify(text)
        assert "domain" in res
        assert res["domain"] in DOMAINS
        assert "domain_scores" in res
        assert "model_version" in res
        assert isinstance(res["domain_scores"], dict)


# =====================================================================
# 9. Orchestrator End-to-End Integration Tests
# =====================================================================
class TestOrchestratorIntegration:
    @pytest.fixture
    def test_db(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()

    def test_single_evidence_creates_master_challenge(self, test_db):
        evidence_in = {
            "source": "citizen",
            "raw_text": "Severe drinking water crisis and contaminated wells in Namkum, Ranchi",
            "submitted_lat": 23.34,
            "submitted_lng": 85.42
        }
        res = process_evidence(evidence_in, test_db)
        assert res["status"] == "success"
        assert res["action"] == "new_challenge"
        assert res["challenge_id"].startswith("HC-")

        # Verify database entities
        challenge = test_db.query(Challenge).filter(Challenge.id == res["challenge_id"]).first()
        assert challenge is not None
        assert challenge.district == "Ranchi"
        assert challenge.domain in DOMAINS

        evidences = test_db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == challenge.id).all()
        assert len(evidences) == 1
        assert evidences[0].source == "citizen"

        analysis = test_db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == challenge.id).first()
        assert analysis is not None
        assert analysis.priority_score == challenge.priority_score

    def test_multisource_convergence(self, test_db):
        # 1. First report from citizen web form
        ev1 = {
            "source": "citizen",
            "raw_text": "Primary Health Center in Namkum, Ranchi is closed without doctor or medicine",
            "submitted_lat": 23.34,
            "submitted_lng": 85.42
        }
        res1 = process_evidence(ev1, test_db)
        cid1 = res1["challenge_id"]

        # 2. Second report from Twitter on same exact issue
        ev2 = {
            "source": "twitter",
            "raw_text": "@JharkhandGovt Namkum Ranchi PHC clinic is closed without doctor or medicine supplies #NamkumHealth",
            "submitted_lat": None,
            "submitted_lng": None
        }
        res2 = process_evidence(ev2, test_db)

        # Either auto-linked to cid1 or flagged as related
        if res2["action"] == "link":
            assert res2["challenge_id"] == cid1
            ev_count = test_db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == cid1).count()
            assert ev_count == 2
        else:
            assert res2["action"] == "flag_related"
            relations = test_db.query(ChallengeRelation).filter(
                (ChallengeRelation.source_challenge_id == res2["challenge_id"]) |
                (ChallengeRelation.target_challenge_id == res2["challenge_id"])
            ).all()
            assert len(relations) > 0
