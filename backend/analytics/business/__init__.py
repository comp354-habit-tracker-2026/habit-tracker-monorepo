# ============================================================
# G13 - toby-fischer - Fitness Indicators - PR #287
# ============================================================
try:
    from .services import AnalyticsService
    __all__ = ["AnalyticsService"]
except ImportError:
    # Allow imports to work even without Django installed (e.g., for testing indicators)
    __all__ = []