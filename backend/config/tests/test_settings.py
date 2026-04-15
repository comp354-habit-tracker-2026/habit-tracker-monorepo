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