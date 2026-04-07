# ============================================================
# G13 - toby-fischer - Fitness Indicators - PR #287
# ============================================================
try:
    from .services import AnalyticsService
    __all__ = ["AnalyticsService"]
except ModuleNotFoundError as exc:
    # Allow imports to work even without Django installed (e.g., for testing indicators)
    if exc.name == "django" or (exc.name and exc.name.startswith("django.")):
        __all__ = []
    else:
        raise