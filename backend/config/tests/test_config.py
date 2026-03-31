"""
Tests for Django configuration and environment variables.

Validates that all configuration values are correctly loaded from
environment variables and use sensible defaults.
"""

import os
from django.test import SimpleTestCase
from django.conf import settings


class EnvironmentVariableTests(SimpleTestCase):
    """Test that all environment variables are properly loaded."""

    def test_django_secret_key_from_env(self):
        """Test DJANGO_SECRET_KEY is loaded from environment."""
        # Should be set in .env
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, '')

    def test_django_debug_from_env(self):
        """Test DJANGO_DEBUG is loaded from environment."""
        # In development, should be True
        self.assertIsInstance(settings.DEBUG, bool)

    def test_django_allowed_hosts_from_env(self):
        """Test DJANGO_ALLOWED_HOSTS is parsed correctly."""
        # Should contain localhost, 127.0.0.1, and 0.0.0.0
        self.assertIn('localhost', settings.ALLOWED_HOSTS)
        self.assertIn('127.0.0.1', settings.ALLOWED_HOSTS)
        self.assertIn('0.0.0.0', settings.ALLOWED_HOSTS)

    def test_database_name_from_env(self):
        """Test POSTGRES_DB is loaded from environment."""
        db_name = settings.DATABASES['default']['NAME']
        self.assertTrue(
            db_name == 'habit_tracker_db' or db_name == 'test_habit_tracker_db',
            f"Unexpected database name: {db_name}",
        )

    def test_database_user_from_env(self):
        """Test POSTGRES_USER is loaded from environment."""
        self.assertEqual(settings.DATABASES['default']['USER'], 'myuser')

    def test_database_password_required(self):
        """Test POSTGRES_PASSWORD must be provided."""
        # Should not have a None value in production
        password = settings.DATABASES['default']['PASSWORD']
        # In test env with .env, it should be set
        self.assertIsNotNone(password)

    def test_database_host_required(self):
        """Test POSTGRES_HOST must be provided."""
        # Should not have a None value in production
        host = settings.DATABASES['default']['HOST']
        # In test env with .env, it should be set
        self.assertIsNotNone(host)

    def test_database_port_from_env(self):
        """Test POSTGRES_PORT is loaded from environment."""
        self.assertEqual(settings.DATABASES['default']['PORT'], '5432')


class EnvironmentVariableEnvFileTests(SimpleTestCase):
    """Tests that verify .env file compliance."""

    def test_env_file_has_all_required_vars(self):
        """Verify .env file contains all required variables."""
        required_vars = [
            'DJANGO_SECRET_KEY',
            'DJANGO_DEBUG',
            'DJANGO_ALLOWED_HOSTS',
            'POSTGRES_DB',
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'POSTGRES_HOST',
            'POSTGRES_PORT',
        ]

        env_path = os.path.join(
            os.path.dirname(__file__),
            '../../.env'
        )

        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()

            for var in required_vars:
                self.assertIn(
                    var,
                    env_content,
                    f"Missing {var} in .env file"
                )


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

    def test_database_port_is_valid_port_number(self):
        """Test database PORT is a valid port number."""
        port = int(settings.DATABASES['default']['PORT'])
        self.assertGreaterEqual(port, 1)
        self.assertLessEqual(port, 65535)

    def test_database_engine_is_postgresql(self):
        """Test database engine is PostgreSQL."""
        engine = settings.DATABASES['default']['ENGINE']
        self.assertEqual(engine, 'django.db.backends.postgresql')

    def test_time_zone_is_valid(self):
        """Test TIME_ZONE is a valid timezone."""
        # Basic check - UTC and en-us are valid
        timezone = settings.TIME_ZONE

        # Valid timezones include UTC and common ones
        valid_zones = ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo']
        self.assertTrue(
            timezone == 'UTC' or timezone in valid_zones or '/' in timezone,
            f"TIME_ZONE '{timezone}' looks invalid"
        )