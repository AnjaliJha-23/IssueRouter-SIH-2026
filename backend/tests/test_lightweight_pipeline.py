"""
backend/tests/test_lightweight_pipeline.py
Unit and integration tests for the lightweight fallback pipeline and import guard.
Verifies that the backend can operate seamlessly without heavy ML dependencies.
"""
import sys
import os
import math
import pytest
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from db.database import Base
from db.models import Challenge, ChallengeEvidence, ChallengeAnalysis, ChallengeRelation
from pipeline.config import DOMAINS, SUBDOMAIN_MAP
from pipeline.lightweight_orchestrator import (
    classify_heuristic,
    extract_entities_gazetteer,
    get_deterministic_embedding,
    process_evidence as process_evidence_lw,
    analyze_challenge as analyze_challenge_lw,
    load_all_models as load_all_models_lw
)
from pipeline import get_active_orchestrator, process_evidence, analyze_challenge


class TestLightweightClassification:
    def test_healthcare_domain(self):
        res = classify_heuristic("Acute medicine shortage and closed hospital clinic in village")
        assert res["domain"] == "Healthcare"
        assert res["model_version"] == "heuristic/keyword-rules-v1"
        assert res["domain_scores"]["Healthcare"] > res["domain_scores"]["Education"]

    def test_water_domain(self):
        res = classify_heuristic("Severe drinking water crisis, broken handpumps and dried borewells")
        assert res["domain"] == "Water & Sanitation"
        assert res["domain_scores"]["Water & Sanitation"] > 0.1

    def test_education_domain(self):
        res = classify_heuristic("Government primary school has no teachers and broken classrooms")
        assert res["domain"] == "Education"

    def test_infrastructure_domain(self):
        res = classify_heuristic("Potholes on highway road and dangerous broken bridge")
        assert res["domain"] == "Infrastructure/Transport"

    def test_energy_domain(self):
        res = classify_heuristic("Burnt electric transformer causing power outage and blackouts")
        assert res["domain"] == "Energy"

    def test_all_domains_present_in_scores(self):
        res = classify_heuristic("General civic complaint")
        assert res["domain"] in DOMAINS
        for d in DOMAINS:
            assert d in res["domain_scores"]


class TestLightweightLocationExtraction:
    def test_district_match(self):
        res = extract_entities_gazetteer("Huge protest in Ranchi regarding drinking water")
        assert res["district"] == "Ranchi"
        assert res["resolution_method"] == "gazetteer_match"
        assert res["confidence"] >= 0.85

    def test_block_match_infers_district(self):
        # Namkum is a block in Ranchi district
        res = extract_entities_gazetteer("Clinic closed in Namkum without notice")
        assert res["block"] == "Namkum"
        assert res["district"] == "Ranchi"

    def test_coordinates_passthrough(self):
        meta = {"latitude": 23.344, "longitude": 85.309}
        res = extract_entities_gazetteer("Random issue without place name", meta)
        assert res["latitude"] == 23.344
        assert res["longitude"] == 85.309


class TestDeterministicEmbedding:
    def test_embedding_dimensions(self):
        emb = get_deterministic_embedding("Sample text for vector generation")
        assert isinstance(emb, list)
        assert len(emb) == 384
        assert all(isinstance(x, float) for x in emb)

    def test_determinism(self):
        text = "Exact same civic distress text"
        emb1 = get_deterministic_embedding(text)
        emb2 = get_deterministic_embedding(text)
        assert emb1 == emb2

    def test_unit_norm(self):
        emb = get_deterministic_embedding("Contaminated water pipeline leak in urban colony")
        norm = math.sqrt(sum(x * x for x in emb))
        assert abs(norm - 1.0) < 1e-4

    def test_empty_string_embedding(self):
        emb = get_deterministic_embedding("")
        assert len(emb) == 384
        norm = math.sqrt(sum(x * x for x in emb))
        assert abs(norm - 1.0) < 1e-4


class TestLightweightPipelineIntegration:
    @pytest.fixture
    def test_db(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()

    def test_process_evidence_creates_records(self, test_db):
        evidence_in = {
            "source": "citizen",
            "title": "Broken Handpump",
            "raw_text": "Drinking water handpump broken in Namkum, Ranchi. Villagers walking 3km for water.",
            "location": "Namkum, Ranchi",
            "submitted_lat": 23.34,
            "submitted_lng": 85.42
        }

        res = process_evidence_lw(evidence_in, test_db)
        assert res["status"] == "success"
        assert res["action"] == "new_challenge"
        assert res["challenge_id"].startswith("CHL-")
        assert res["domain"] == "Water & Sanitation"
        assert res["district"] == "Ranchi"
        assert res["priority_score"] > 0
        assert "analysis" in res
        assert res["analysis"]["model_versions"]["classification"] == "heuristic/keyword-rules-v1"

        # Verify DB records
        ch = test_db.query(Challenge).filter(Challenge.id == res["challenge_id"]).first()
        assert ch is not None
        assert ch.domain == "Water & Sanitation"
        assert ch.district == "Ranchi"

        evs = test_db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == ch.id).all()
        assert len(evs) == 1
        assert len(evs[0].embedding_json) == 384

        an = test_db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == ch.id).first()
        assert an is not None
        assert an.priority_score == ch.priority_score

    def test_analyze_challenge_recalculation(self, test_db):
        evidence_in = {
            "source": "citizen",
            "raw_text": "Severe medicine stockout at PHC hospital clinic in Ranchi",
            "submitted_lat": 23.34,
            "submitted_lng": 85.42
        }
        res = process_evidence_lw(evidence_in, test_db)
        cid = res["challenge_id"]

        re_res = analyze_challenge_lw(cid, test_db)
        assert re_res["status"] == "success"
        assert re_res["challenge_id"] == cid
        assert re_res["domain"] == "Healthcare"
        assert re_res["priority_score"] > 0


class TestStartupGuardAndDispatch:
    def test_default_orchestrator_is_lightweight(self, monkeypatch):
        monkeypatch.delenv("ENABLE_HEAVY_ML", raising=False)
        orch = get_active_orchestrator()
        from pipeline import lightweight_orchestrator
        assert orch is lightweight_orchestrator

    def test_graceful_fallback_when_heavy_fails(self, monkeypatch):
        monkeypatch.setenv("ENABLE_HEAVY_ML", "true")
        # Even if heavy is requested, if an import fails it must safely return lightweight
        orch = get_active_orchestrator()
        assert orch is not None
        assert hasattr(orch, "process_evidence")
        assert hasattr(orch, "analyze_challenge")

    def test_strict_heavy_ml_dependency_isolation(self):
        """
        Simulate an environment where heavy ML packages are missing.
        Verify that lightweight processing succeeds without them.
        """
        class BlockImporter:
            blocked = {'torch', 'transformers', 'sentence_transformers', 'spacy', 'huggingface_hub', 'tokenizers'}
            def find_spec(self, fullname, path, target=None):
                root = fullname.split('.')[0]
                if root in self.blocked:
                    raise ModuleNotFoundError(f"No module named '{fullname}' (simulated isolated env)")
                return None

        importer = BlockImporter()
        sys.meta_path.insert(0, importer)
        try:
            from pipeline.lightweight_orchestrator import classify_heuristic, get_deterministic_embedding, extract_entities_gazetteer
            c = classify_heuristic("Water leakage and broken handpump in Ranchi")
            assert c["domain"] == "Water & Sanitation"
            e = get_deterministic_embedding("Sample text")
            assert len(e) == 384
            loc = extract_entities_gazetteer("Issue in Ranchi")
            assert loc["district"] == "Ranchi"
        finally:
            if importer in sys.meta_path:
                sys.meta_path.remove(importer)
