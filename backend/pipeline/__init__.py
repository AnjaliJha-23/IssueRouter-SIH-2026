def process_evidence(*args, **kwargs):
    from .orchestrator import process_evidence as _pe
    return _pe(*args, **kwargs)

def analyze_challenge(*args, **kwargs):
    from .orchestrator import analyze_challenge as _ac
    return _ac(*args, **kwargs)

def load_all_models(*args, **kwargs):
    from .orchestrator import load_all_models as _lam
    return _lam(*args, **kwargs)

__all__ = ["process_evidence", "analyze_challenge", "load_all_models"]