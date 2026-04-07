# ============================================================
# G13 - toby-fischer - Fitness Indicators - PR #287
# ============================================================
__all__ = []

try:
    from .services import AnalyticsService
except ModuleNotFoundError as exc:
    # Allow imports to work in environments where Django is not installed
    if not (exc.name == "django" or (exc.name and exc.name.startswith("django."))):
        raise
else:
    __all__.append("AnalyticsService")