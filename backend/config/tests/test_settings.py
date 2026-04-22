import importlib

def reload_settings():
    project_settings = importlib.import_module('config.settings')
    return importlib.reload(project_settings)

def test_allowed_hosts_include_platform_host_env_vars(monkeypatch):
    """Ensure platform-provided host env vars are appended to default hosts."""
    with monkeypatch.context() as m:
        m.setenv('DJANGO_ALLOWED_HOSTS', 'example.com,api.example.com')

        settings = reload_settings()

        assert settings.ALLOWED_HOSTS == ['example.com', 'api.example.com']

    # Reload once more after env vars are restored to avoid leaking module state.
    importlib.reload(settings)

def test_allowed_hosts_env_override(monkeypatch):
    monkeypatch.setenv('DJANGO_ALLOWED_HOSTS', 'example.com,api.example.com')

    reloaded = importlib.reload(reload_settings())

    assert reloaded.ALLOWED_HOSTS == ['example.com', 'api.example.com']

def test_allowed_hosts_strips_empty_values(monkeypatch):
    monkeypatch.setenv('DJANGO_ALLOWED_HOSTS', 'example.com,, ,api.example.com')

    reloaded = importlib.reload(reload_settings())

    assert reloaded.ALLOWED_HOSTS == ['example.com', 'api.example.com']


def test_production_database_config(monkeypatch):
    """Force the environment to 'prod' to test the Postgres config block."""
    monkeypatch.setenv('ENVIRONMENT', 'prod')
    monkeypatch.setenv('POSTGRES_DB', 'prod_db')
    monkeypatch.setenv('POSTGRES_USER', 'prod_user')
    monkeypatch.setenv('POSTGRES_PASSWORD', 'prod_pass')

    # Reload to trigger the 'if ENVIRONMENT == "prod"' block
    settings = reload_settings()

    assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'
    assert settings.DATABASES['default']['NAME'] == 'prod_db'


def test_allowed_hosts_defaults_when_env_var_empty(monkeypatch):
    """Test the 'else' branch when DJANGO_ALLOWED_HOSTS is not set."""
    monkeypatch.delenv('DJANGO_ALLOWED_HOSTS', raising=False)
    settings = reload_settings()

    # Verify it falls back to default_allowed_hosts + platform_hosts
    assert 'localhost' in settings.ALLOWED_HOSTS
    assert '127.0.0.1' in settings.ALLOWED_HOSTS