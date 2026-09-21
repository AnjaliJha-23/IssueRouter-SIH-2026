import os
import logging

logger = logging.getLogger(__name__)

def get_active_orchestrator():
    """
    Selects the active pipeline orchestrator.
    - If ENABLE_HEAVY_ML is 'true'/'1', attempts to load the full heavy ML orchestrator.
    - If heavy dependencies fail to import or ENABLE_HEAVY_ML is false/unset,
      falls back safely to lightweight_orchestrator (0 heavy dependencies).
    """
    enable_heavy = os.getenv("ENABLE_HEAVY_ML", "false").lower() in ("true", "1")
    if enable_heavy:
        try:
            from . import orchestrator
            return orchestrator
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(
                f"[Pipeline Guard] Heavy ML requested (ENABLE_HEAVY_ML=true) but dependencies could not be loaded: {e}. "
                f"Falling back safely to lightweight pipeline."
            )

    from . import lightweight_orchestrator
    return lightweight_orchestrator

def process_evidence(*args, **kwargs):
    orch = get_active_orchestrator()
    return orch.process_evidence(*args, **kwargs)

def analyze_challenge(*args, **kwargs):
    orch = get_active_orchestrator()
    return orch.analyze_challenge(*args, **kwargs)

def load_all_models(*args, **kwargs):
    orch = get_active_orchestrator()
    return orch.load_all_models(*args, **kwargs)

__all__ = ["process_evidence", "analyze_challenge", "load_all_models", "get_active_orchestrator"]