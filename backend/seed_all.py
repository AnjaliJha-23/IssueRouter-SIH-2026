"""
seed_all.py - Runs all required seeders to populate the database fully.
"""
import sys
from pathlib import Path

# Add backend dir to python path
sys.path.insert(0, str(Path(__file__).parent))

import seed_mock_data
import seed_universities

if __name__ == "__main__":
    db_path = Path(__file__).parent / "issueRouter.db"
    if db_path.exists():
        print(f"Deleting existing database: {db_path}")
        db_path.unlink()
        
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
