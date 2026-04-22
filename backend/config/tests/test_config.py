"""
Tests for Django configuration and environment variables.

Validates that required configuration values are correctly loaded from
environment variables and corresponding .env file entries.
"""

from django.test import SimpleTestCase
from django.conf import settings


class EnvironmentVariableTests(SimpleTestCase):
    """Test that all environment variables are properly loaded."""

    def test_django_secret_key_from_env(self):
        """Test DJANGO_SECRET_KEY is loaded from environment."""
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, '')

    def test_django_debug_from_env(self):
        """Test DJANGO_DEBUG is loaded from environment."""
        self.assertIsInstance(settings.DEBUG, bool)

    def test_django_allowed_hosts_from_env(self):
        """Test DJANGO_ALLOWED_HOSTS is parsed correctly."""
        self.assertIn('localhost', settings.ALLOWED_HOSTS)
        self.assertIn('127.0.0.1', settings.ALLOWED_HOSTS)
        self.assertIn('0.0.0.0', settings.ALLOWED_HOSTS)

    def test_database_name_is_present(self):
        """Database name should always be configured."""
        db_name = settings.DATABASES['default']['NAME']
        self.assertIsNotNone(db_name)
        self.assertNotEqual(db_name, '')

    def test_database_password_required(self):
        """Database password should be defined or intentionally blank in test sqlite."""
        password = settings.DATABASES['default'].get('PASSWORD')
        self.assertIsNotNone(password)

    def test_database_host_required(self):
        """Database host key should exist even if blank for sqlite tests."""
        host = settings.DATABASES['default'].get('HOST')
        self.assertIsNotNone(host)


class ConfigurationConsistencyTests(SimpleTestCase):
    """Tests that validate configuration consistency."""

    def test_jwt_timedelta_values_are_positive(self):
        """Test JWT token lifetimes are positive durations."""
        access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

        self.assertGreater(access_lifetime.total_seconds(), 0)
        self.assertGreater(refresh_lifetime.total_seconds(), 0)

    def test_access_token_shorter_than_refresh_token(self):
        """Test access token lifetime is shorter than refresh token."""
        access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

        self.assertLess(
            access_lifetime.total_seconds(),
            refresh_lifetime.total_seconds(),
            "Access token lifetime should be shorter than refresh token lifetime"
        )

    def test_page_size_is_positive_integer(self):
        """Test PAGE_SIZE is a positive integer."""
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        self.assertIsInstance(page_size, int)
        self.assertGreater(page_size, 0)

    def test_database_engine_is_supported(self):
        """Test database engine is one of the supported backends."""
        engine = settings.DATABASES['default']['ENGINE']
        self.assertIn(
            engine,
            ['django.db.backends.postgresql', 'django.db.backends.sqlite3']
        )

    def test_database_port_is_valid_when_provided(self):
        """Test database PORT is valid when the backend uses one."""
        port = settings.DATABASES['default'].get('PORT', '')
        engine = settings.DATABASES['default']['ENGINE']

        if engine == 'django.db.backends.sqlite3':
            self.assertIn(port, ['', None])
        else:
            port_num = int(port)
            self.assertGreaterEqual(port_num, 1)
            self.assertLessEqual(port_num, 65535)

    def test_time_zone_is_valid(self):
        """Test TIME_ZONE is a valid timezone."""
        timezone = settings.TIME_ZONE
        valid_zones = ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo']
        self.assertTrue(
            timezone == 'UTC' or timezone in valid_zones or '/' in timezone,
            f"TIME_ZONE '{timezone}' looks invalid"
        )