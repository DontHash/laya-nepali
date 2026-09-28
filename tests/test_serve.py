from __future__ import annotations

from unittest.mock import MagicMock

import pytest

try:
    from starlette.testclient import TestClient
    from layanep import serve
    HAS_SERVE = True
except ImportError:
    HAS_SERVE = False

pytestmark = pytest.mark.skipif(
    not HAS_SERVE,
    reason="serving extras not installed (install with pip install -e '.[serve]')",
)


@pytest.fixture
def client() -> TestClient:
    app = serve.create_app()
    return TestClient(app)


def test_health_no_model(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "no_model"
    assert data["domain"] == "restaurant"


def test_system_one_no_model(client: TestClient) -> None:
    resp = client.post("/v1/systemone", json={"state": {"body": "नमस्ते"}})
    assert resp.status_code == 503
    assert resp.json() == {"error": "model not loaded"}


def test_message_no_model(client: TestClient) -> None:
    resp = client.post("/v1/message", json={"text": "नमस्ते"})
    assert resp.status_code == 503
    assert resp.json() == {"error": "model not loaded"}


def test_message_with_mock_agent_restaurant() -> None:
    mock_agent = MagicMock()
    mock_agent.system_one.return_value = {
        "answers": {
            "command": {
                "choice": "greet",
                "answer_confidence": 0.95,
                "probabilities": {"greet": 0.95, "none": 0.01},
            },
            "needs_staff": {"choice": "false"},
            "abstain": {"choice": "false"},
        }
    }

    original_agent = serve._agent
    original_config = serve._config
    try:
        serve._agent = mock_agent
        serve._config = {"abstain_threshold": 0.4, "abstain_p_none": 0.02, "model_name": "mock-laya"}
        app = serve.create_app(domain="restaurant")
        c = TestClient(app)

        resp = client_resp = c.post(
            "/v1/message",
            json={
                "text": "नमस्ते",
                "business_name": "Sherpa Kitchen",
                "business_state": {"business": {"name": "Sherpa Kitchen"}},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] == "greet"
        assert data["tier"] == 0
        assert data["auto_served"] is True
        assert "Sherpa Kitchen" in data["reply"]
    finally:
        serve._agent = original_agent
        serve._config = original_config


def test_message_with_mock_agent_clothing() -> None:
    mock_agent = MagicMock()
    mock_agent.system_one.return_value = {
        "answers": {
            "command": {
                "choice": "catalog",
                "answer_confidence": 0.96,
                "probabilities": {"catalog": 0.96, "none": 0.005},
            },
            "needs_staff": {"choice": "false"},
            "abstain": {"choice": "false"},
        }
    }

    original_agent = serve._agent
    original_config = serve._config
    try:
        serve._agent = mock_agent
        serve._config = {"abstain_threshold": 0.4, "abstain_p_none": 0.02, "model_name": "mock-clothing-laya"}
        app = serve.create_app(domain="clothing")
        c = TestClient(app)

        resp = c.post(
            "/v1/message",
            json={
                "text": "कपडाहरु के के छन्?",
                "business_name": "Hamro Fashion",
                "business_state": {
                    "business": {
                        "name": "Hamro Fashion",
                        "catalog": [{"name": "कुर्था"}, {"name": "हुडी"}],
                    }
                },
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] == "catalog"
        assert data["tier"] == 0
        assert data["auto_served"] is True
        assert "कुर्था" in data["reply"]
    finally:
        serve._agent = original_agent
        serve._config = original_config
