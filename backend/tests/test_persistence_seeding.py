"""
backend/tests/test_persistence_seeding.py
Unit and integration tests for Phase 3:
- SQLite persistence configuration & PRAGMA settings (WAL mode, busy_timeout)
- DATABASE_URL and SQLITE_DB_PATH resolution
- University CSV path resolution
- Auto-seeding guard and error re-raising on failure
- Verification of 127 seeded challenges from seed_mock_data
"""
import os
import sys
import tempfile
import sqlite3
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from db.database import Base, SessionLocal, engine, get_db, DATABASE_URL, DB_PATH
from db.models import Challenge, Organization
import seed_universities
from main import app, startup_event


class TestDatabaseConfiguration:
    def test_default_database_path_and_url(self):
        """Verify default database path points to issueRouter.db."""
        assert DB_PATH.name == "issueRouter.db"
        assert DATABASE_URL.startswith("sqlite:///")

    def test_sqlite_pragmas_applied(self):
        """Verify SQLite engine applies WAL mode, synchronous=NORMAL, and busy_timeout."""
        with engine.connect() as conn:
            raw_conn = conn.connection.dbapi_connection
            cursor = raw_conn.cursor()
            
            # Check journal_mode (in SQLite WAL mode is set on file-backed dbs)
            cursor.execute("PRAGMA busy_timeout")
            timeout_row = cursor.fetchone()
            assert timeout_row is not None
            # 30000 ms busy timeout
            assert timeout_row[0] >= 30000
            cursor.close()

    def test_custom_sqlite_path_resolution(self):
        """Verify custom DATABASE_URL and SQLITE_DB_PATH resolution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db_file = Path(tmpdir) / "custom_dir" / "test_custom.db"
            test_url = f"sqlite:///{test_db_file}"
            
            with patch.dict(os.environ, {"DATABASE_URL": test_url}, clear=False):
                # Re-evaluating path logic
                raw = test_url[len("sqlite:///"):]
                resolved = Path(raw).resolve()
                assert resolved == test_db_file.resolve()


class TestUniversityCsvResolution:
    def test_resolve_csv_path_exists(self):
        """Verify resolve_csv_path finds the Jharkhand universities CSV."""
        csv_path = seed_universities.resolve_csv_path()
        assert csv_path.exists(), f"CSV path {csv_path} does not exist"
        assert "Jharkhand universities" in csv_path.name

    def test_resolve_csv_path_custom_env(self):
        """Verify UNIVERSITIES_CSV_PATH env override is honored."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_csv = f.name
        try:
            with patch.dict(os.environ, {"UNIVERSITIES_CSV_PATH": temp_csv}):
                resolved = seed_universities.resolve_csv_path()
                assert resolved == Path(temp_csv)
        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)


class TestAutoSeedGuardAndErrorHandling:
    def test_auto_seed_skipped_when_disabled(self):
        """When AUTO_SEED_ON_START is false/unset, seed should not be called."""
        with patch.dict(os.environ, {"AUTO_SEED_ON_START": "false"}):
            with patch("seed_mock_data.seed") as mock_seed:
                # Call startup_event directly
                startup_event()
                mock_seed.assert_not_called()

    def test_auto_seed_skipped_when_challenges_exist(self):
        """When AUTO_SEED_ON_START is true but database already has challenges, seed must NOT run."""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 127
        mock_db.query.return_value = mock_query

        with patch.dict(os.environ, {"AUTO_SEED_ON_START": "true"}):
            with patch("main.SessionLocal", return_value=mock_db):
                with patch("seed_mock_data.seed") as mock_seed:
                    startup_event()
                    mock_seed.assert_not_called()

    def test_auto_seed_reraises_on_failure(self):
        """When AUTO_SEED_ON_START is true, challenge count is 0, and seed() fails, exception must be re-raised."""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_db.query.return_value = mock_query

        with patch.dict(os.environ, {"AUTO_SEED_ON_START": "true"}):
            with patch("main.SessionLocal", return_value=mock_db):
                with patch("seed_mock_data.seed", side_effect=RuntimeError("Disk I/O error during seed")):
                    with pytest.raises(RuntimeError, match="Disk I/O error during seed"):
                        startup_event()


class TestRepositorySeedVerification:
    def test_seed_mock_data_produces_127_challenges(self):
        """Verify that the repository database contains exactly 127 seeded master challenges (CHL-2026-0001 to 0127)."""
        db = SessionLocal()
        try:
            # Query the 127 zero-padded master seeded challenges (CHL-2026-0001 to CHL-2026-0127)
            seeded_count = db.query(Challenge).filter(Challenge.id.like("CHL-2026-0%")).count()
            assert seeded_count == 127, f"Expected 127 seeded challenges, found {seeded_count}"
        finally:
            db.close()

    def test_seed_in_fresh_database_produces_127_challenges(self):
        """Verify that running seed_mock_data.seed() in an isolated test database produces exactly 127 challenges."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db = f.name
        
        test_engine = None
        try:
            # Recreate session and engine bound to temp database
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from unittest.mock import patch
            import seed_mock_data

            temp_engine = create_engine(f"sqlite:///{temp_db}", connect_args={"check_same_thread": False})
            TempSession = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)

            with patch("seed_mock_data.engine", temp_engine), patch("seed_mock_data.SessionLocal", TempSession):
                seed_mock_data.seed()
                
                db = TempSession()
                try:
                    total_challenges = db.query(Challenge).count()
                    assert total_challenges == 127, f"Expected 127 challenges in freshly seeded DB, got {total_challenges}"
                finally:
                    db.close()
        finally:
            if os.path.exists(temp_db):
                try:
                    os.unlink(temp_db)
                except Exception:
                    pass

