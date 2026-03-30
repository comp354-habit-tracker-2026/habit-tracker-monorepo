import importlib

def test_allowed_hosts_include_platform_host_env_vars(monkeypatch):
    """Ensure platform-provided host env vars are appended to default hosts."""
    host_values = {
        'WEBSITE_HOSTNAME': 'web.example.com',
        'CONTAINER_APP_HOSTNAME': 'container.example.com',
        'HOSTNAME': 'runtime-host',
    }

    project_settings = importlib.import_module('config.settings')

    with monkeypatch.context() as m:
        m.delenv('DJANGO_ALLOWED_HOSTS', raising=False)
        for env_name, env_value in host_values.items():
            m.setenv(env_name, env_value)

        reloaded_settings = importlib.reload(project_settings)

        for env_value in host_values.values():
            assert env_value in reloaded_settings.default_allowed_hosts
            assert env_value in reloaded_settings.ALLOWED_HOSTS

    # Reload once more after env vars are restored to avoid leaking module state.
    importlib.reload(project_settings)