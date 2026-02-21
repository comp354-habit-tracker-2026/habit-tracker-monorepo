import pytest

@pytest.mark.django_db
def test_health_endpoint(client):
    resp = client.get("/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}