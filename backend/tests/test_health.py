def test_health_and_initial_capabilities(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    capabilities = client.get("/api/capabilities")
    assert capabilities.status_code == 200
    assert capabilities.json()["capabilities"]["jobs"] == "ready"
    assert capabilities.json()["capabilities"]["resumes"] == "ready"
