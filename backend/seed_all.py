"""
seed_all.py - Runs all required seeders to populate the database fully.
"""
import sys
from pathlib import Path

# Add backend dir to python path
sys.path.insert(0, str(Path(__file__).parent))

import seed_mock_data
import seed_universities

import os

if __name__ == "__main__":
    db_path = Path(__file__).parent / "issueRouter.db"
    # Protect against accidental database deletion in non-development environments
    allow_wipe = os.getenv("ALLOW_DB_WIPE", "true").lower() in ("1", "true", "yes")
    
    if db_path.exists() and allow_wipe:
        try:
            print(f"Deleting existing database: {db_path}")
            db_path.unlink()
        except PermissionError:
            print(f"Database file is locked by active server process; proceeding with transaction-level table wipe.")
    elif db_path.exists() and not allow_wipe:
        print(f"Database file exists ({db_path}); skipping file unlink because ALLOW_DB_WIPE=false.")
        
    print("===========================================")
    print("        RUNNING ALL SEED SCRIPTS           ")
    print("===========================================")
    
    # Run seed_mock_data first because it wipes the tables clean
    print("\n--- 1. Seeding Mock Challenges and Matches ---")
    seed_mock_data.seed()
    
    # Run seed_universities second so it adds the real CSV universities 
    # to the freshly wiped and mocked database
    print("\n--- 2. Seeding Real Universities from CSV ---")
    seed_universities.seed()
    
    print("\n===========================================")
    print("        ALL SEEDING COMPLETE!              ")
    print("===========================================")
