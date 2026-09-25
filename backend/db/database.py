"""
db/database.py — SQLAlchemy engine, session factory, and Base for IssueRouter.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# Resolve database URL and file path
_env_db_url = os.getenv("DATABASE_URL")
_env_sqlite_path = os.getenv("SQLITE_DB_PATH")

if _env_db_url:
    DATABASE_URL = _env_db_url
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if DATABASE_URL.startswith("sqlite:///"):
        _raw_path = DATABASE_URL[len("sqlite:///"):]
        if _raw_path and not _raw_path.startswith(":memory:"):
            DB_PATH = Path(_raw_path).resolve()
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        else:
            DB_PATH = Path(__file__).resolve().parent.parent / "issueRouter.db"
    else:
        DB_PATH = Path(__file__).resolve().parent.parent / "issueRouter.db"
elif _env_sqlite_path:
    DB_PATH = Path(_env_sqlite_path).resolve()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    # Default: store DB file at project root (backend/../issueRouter.db)
    DB_PATH = Path(__file__).resolve().parent.parent / "issueRouter.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"

is_sqlite = DATABASE_URL.startswith("sqlite")

connect_args = {}
if is_sqlite:
    connect_args = {
        "check_same_thread": False,  # Needed for SQLite + multi-threaded FastAPI
        "timeout": 30.0,             # Connection timeout in seconds
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

# Configure WAL mode and busy_timeout for SQLite engines
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=30000")
        except Exception:
            pass
        finally:
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

