import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.services.analysis_cache_service import AnalysisCacheService


@pytest.fixture
def cache():
    return AnalysisCacheService(ttl_seconds=60, max_size=100)


class TestAnalysisCacheService:
    def test_get_miss(self, cache):
        result = cache.get(1, 2)
        assert result is None

    def test_set_and_get(self, cache):
        cache.set(1, 2, {"score": 85})
        result = cache.get(1, 2)
        assert result is not None
        assert result["score"] == 85

    def test_invalidate(self, cache):
        cache.set(1, 2, {"score": 85})
        cache.invalidate(1, 2)
        assert cache.get(1, 2) is None

    def test_hit_count(self, cache):
        cache.set(1, 2, {"score": 85})
        cache.get(1, 2)
        cache.get(1, 2)
        cache.get(3, 4)
        assert cache._hits == 2
        assert cache._misses == 1

    def test_hit_rate(self, cache):
        cache.set(1, 2, {"score": 85})
        cache.get(1, 2)
        cache.get(1, 2)
        cache.get(3, 4)
        assert cache.get_hit_rate() == 2 / 3

    def test_clear(self, cache):
        cache.set(1, 2, {"score": 85})
        cache.get(1, 2)
        cache.get(3, 4)
        cache.clear()
        assert cache.get_stats()["cache_size"] == 0
        assert cache._hits == 0
        assert cache._misses == 0

    def test_get_stats(self, cache):
        cache.set(1, 2, {"score": 85})
        cache.get(1, 2)
        stats = cache.get_stats()
        assert stats["cache_size"] == 1
        assert stats["hits"] == 1
        assert stats["ttl_seconds"] == 60
        assert stats["max_size"] == 100

    def test_max_size_eviction(self, cache):
        for i in range(105):
            cache.set(1, i + 10, {"score": i})
        assert len(cache._cache) <= 100


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, TestingSessionLocal


def test_cache_stats_endpoint(client):
    test_client, _ = client

    resp = test_client.get("/api/system/cache/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert "cache_size" in data
    assert "hits" in data
    assert "misses" in data
    assert "hit_rate" in data


def test_cache_clear_endpoint(client):
    test_client, _ = client

    resp = test_client.post("/api/system/cache/clear")

    assert resp.status_code == 200
    assert resp.json()["cleared"] is True


def test_pool_stats_endpoint(client):
    test_client, _ = client

    resp = test_client.get("/api/system/pool/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert "max_workers" in data
    assert "active_tasks" in data
    assert "completed_tasks" in data
