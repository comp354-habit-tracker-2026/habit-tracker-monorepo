"""
Test settings – inherits everything from the main settings but swaps
PostgreSQL for an in-memory SQLite database so tests can run locally
without Docker or a running Postgres instance.
"""

from config.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
