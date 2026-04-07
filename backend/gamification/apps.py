from django.apps import AppConfig


class GamificationConfig(AppConfig):
    name = 'gamification'

    def ready(self):
        import gamification.signals  # noqa: F401
