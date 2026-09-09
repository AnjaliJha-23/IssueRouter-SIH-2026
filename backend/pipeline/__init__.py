def process_evidence(*args, **kwargs):
    from .orchestrator import process_evidence as _pe
    return _pe(*args, **kwargs)

def load_all_models(*args, **kwargs):
    from .orchestrator import load_all_models as _lam
    return _lam(*args, **kwargs)

__all__ = ["process_evidence", "load_all_models"]