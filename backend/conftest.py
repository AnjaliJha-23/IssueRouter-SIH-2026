import sys
import os

# Ensure backend root is always in sys.path for pytest and test runners
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Tests must never depend on an external service or on ~1.6 GB of local model
# weights. Pin the deterministic offline classifier and drop the decision-model
# key, unless the caller explicitly opts into a live Jev test.
if os.getenv("JEV_LIVE_TEST", "").strip().lower() not in ("1", "true", "yes"):
    os.environ["CLASSIFIER_BACKEND"] = "keyword"
    os.environ.pop("TYPESAFE_API_KEY", None)

# Embedding tests are pinned to the local model for the same reason: the hosted
# NVIDIA backend needs a key and a network round trip. Set EMBED_LIVE_TEST=1
# (plus NVIDIA_API_KEY) to exercise the hosted backend instead.
if os.getenv("EMBED_LIVE_TEST", "").strip().lower() not in ("1", "true", "yes"):
    os.environ["EMBEDDING_BACKEND"] = "local_minilm"
    os.environ.pop("NVIDIA_API_KEY", None)
