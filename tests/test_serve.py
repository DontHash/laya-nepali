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
    assert data["max_len"] is None
    assert data["head_max_len"] is None


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


def test_message_uses_training_state_key() -> None:
    """The encoder must see the same state key the dataset and notebook serialise.

    `body` was a train/serve divergence found in the 2026-10-09 audit: every
    training row and the published benchmark use `customer_message`.
    """
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
        app = serve.create_app(domain="clothing")
        c = TestClient(app)

        resp = c.post("/v1/message", json={"text": "नमस्ते"})
        assert resp.status_code == 200
        assert mock_agent.system_one.call_args.args[0] == {"customer_message": "नमस्ते"}
    finally:
        serve._agent = original_agent
        serve._config = original_config


def test_api_key_enforced_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("LAYA_API_KEY", "test-secret-key")
    app = serve.create_app(domain="clothing")
    c = TestClient(app)

    assert c.get("/health").status_code == 200

    unauthorized = c.post("/v1/systemone", json={"state": {"body": "hi"}})
    assert unauthorized.status_code == 401
    assert unauthorized.json() == {"error": "unauthorized"}

    wrong = c.post(
        "/v1/systemone",
        json={"state": {"body": "hi"}},
        headers={"authorization": "Bearer wrong-key"},
    )
    assert wrong.status_code == 401

    authorized = c.post(
        "/v1/systemone",
        json={"state": {"body": "hi"}},
        headers={"authorization": "Bearer test-secret-key"},
    )
    assert authorized.status_code == 503  # authorized, but no model loaded


def test_health_exposes_effective_thresholds_and_limits() -> None:
    original_config = serve._config
    try:
        serve._config = {
            "abstain_threshold": 0.9,
            "abstain_p_none": 0.02,
            "max_len": 1024,
            "head_max_len": 256,
            "model_name": "laya-nepali-clothing-v1",
            "fine_tuned": True,
        }
        c = TestClient(serve.create_app(domain="clothing"))
        data = c.get("/health").json()
        assert data["tau"] == 0.9
        assert data["p_none_max"] == 0.02
        assert data["max_len"] == 1024
        assert data["head_max_len"] == 256
        assert data["model"] == "laya-nepali-clothing-v1"
        assert data["fine_tuned"] is True
    finally:
        serve._config = original_config


def test_unknown_app_domain_fails_fast() -> None:
    with pytest.raises(KeyError):
        serve.create_app(domain="garden")


def test_unknown_request_domain_returns_422() -> None:
    mock_agent = MagicMock()
    mock_agent.system_one.return_value = {"answers": {}}
    original_agent = serve._agent
    original_config = serve._config
    try:
        serve._agent = mock_agent
        serve._config = {"abstain_threshold": 0.4, "abstain_p_none": 0.02}
        c = TestClient(serve.create_app(domain="clothing"))
        resp = c.post("/v1/message", json={"text": "hi", "domain": "garden"})
        assert resp.status_code == 422
        assert "unknown domain" in resp.json()["error"]
        resp2 = c.post("/v1/systemone", json={"state": {"customer_message": "hi"}, "domain": "garden"})
        assert resp2.status_code == 422
    finally:
        serve._agent = original_agent
        serve._config = original_config
