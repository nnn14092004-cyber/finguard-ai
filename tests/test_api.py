"""Integration test suite for FinGuard-AI FastAPI REST gateway endpoints."""

from __future__ import annotations

import io

from fastapi.testclient import TestClient

from src.api.app import app
from src.domain.enums import RiskTier

client = TestClient(app)


def test_api_root_discovery() -> None:
    """Verifies that root discovery endpoint returns service navigation metadata."""
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "operational"
    assert "documentation" in payload
    assert payload["service"] == "FinGuard-AI Regulatory Gateway"
    assert "endpoints" in payload


def test_api_health_check() -> None:
    """Verifies that the /health endpoint reports operational status."""
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == "FinGuard-AI Regulatory Gateway"
    assert "version" in payload


def test_api_audit_text_successful_red_flag() -> None:
    """Verifies text auditing endpoint identifies predatory high-yield contract."""
    raw_payload = {
        "document_title": "synthetic_scam_promo.txt",
        "content": (
            "Guaranteed 2.5% daily return on algorithmic trading with 100% capital guaranteed. "
            "Members receive binary bonuses and multi-tier downline commission. "
            "Mandatory lock-up period of 24 months applies with early withdrawal penalty of 40%. "
            "Governed by the laws of Seychelles."
        ),
    }

    response = client.post("/api/v1/audit/text", json=raw_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["risk_tier"] == RiskTier.RED_FLAG.value
    assert data["suspicion_score"] >= 75
    assert data["total_findings"] > 0
    assert len(data["remediation_actions"]) > 0


def test_api_audit_text_validation_failure() -> None:
    """Verifies that blank or whitespace contract content is rejected with 422."""
    raw_payload = {"document_title": "empty.txt", "content": "   \n\t  "}
    response = client.post("/api/v1/audit/text", json=raw_payload)
    assert response.status_code == 422


def test_api_audit_file_upload() -> None:
    """Verifies contract document upload analysis returns green tier for commercial SLA."""
    contract_bytes = (
        b"Enterprise Cloud Service Level Agreement. "
        b"99.9% uptime commitment with standard 30-day termination notice. "
        b"Governed by Delaware state law."
    )

    files = {"file": ("enterprise_agreement.txt", io.BytesIO(contract_bytes), "text/plain")}
    response = client.post("/api/v1/audit/file", files=files)
    assert response.status_code == 200
    data = response.json()

    assert data["risk_tier"] == RiskTier.GREEN.value
    assert data["suspicion_score"] < 25


def test_api_audit_file_empty_rejection() -> None:
    """Verifies that zero-byte uploaded file is rejected with 422."""
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    response = client.post("/api/v1/audit/file", files=files)
    assert response.status_code == 422
