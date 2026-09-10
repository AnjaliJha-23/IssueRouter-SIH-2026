import sys
import os

# Ensure backend root is always in sys.path for pytest and test runners
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
