"""Integration & Unit Test Suite for FinGuard-AI FastAPI REST Gateway.

Verifies root discovery, health check, text auditing, and file upload analysis.
"""

from __future__ import annotations

import asyncio
import io
import pytest

from fastapi import HTTPException, UploadFile
from src.api.app import app, audit_file, audit_text, health_check, root
from src.domain.enums import RiskTier
from src.domain.models import ContractAuditRequest

try:
    from starlette.testclient import TestClient

    client = TestClient(app)
    HAS_TESTCLIENT = True
except (ImportError, RuntimeError):
    client = None
    HAS_TESTCLIENT = False


def test_api_root_discovery() -> None:
    """Verifies that root discovery endpoint returns service navigation metadata."""
    if HAS_TESTCLIENT and client is not None:
        response = client.get("/")
        assert response.status_code == 200
        payload = response.json()
    else:
        payload = asyncio.run(root())

    assert payload["status"] == "operational"
    assert "documentation" in payload
    assert "endpoints" in payload


def test_api_health_check() -> None:
    """Verifies that the /health endpoint reports operational status."""
    if HAS_TESTCLIENT and client is not None:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
    else:
        payload = asyncio.run(health_check())

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

    if HAS_TESTCLIENT and client is not None:
        response = client.post("/api/v1/audit/text", json=raw_payload)
        assert response.status_code == 200
        report = response.json()
        assert report["file_name"] == "synthetic_scam_promo.txt"
        assert report["suspicion_score"] >= 75
        assert report["risk_tier"] == RiskTier.RED_FLAG.value
        assert report["total_findings"] >= 3
    else:
        req = ContractAuditRequest(**raw_payload)
        report_obj = asyncio.run(audit_text(req))
        assert report_obj.file_name == "synthetic_scam_promo.txt"
        assert report_obj.suspicion_score >= 75
        assert report_obj.risk_tier == RiskTier.RED_FLAG
        assert report_obj.total_findings >= 3


def test_api_audit_text_validation_failure() -> None:
    """Verifies defensive rejection on blank or whitespace payloads."""
    empty_payload = {
        "document_title": "empty.txt",
        "content": "     \n\t   ",
    }

    if HAS_TESTCLIENT and client is not None:
        response = client.post("/api/v1/audit/text", json=empty_payload)
        assert response.status_code == 422
    else:
        with pytest.raises(HTTPException) as exc_info:
            req = ContractAuditRequest(**empty_payload)
            asyncio.run(audit_text(req))
        assert exc_info.value.status_code == 422


def test_api_audit_file_upload() -> None:
    """Verifies contract document upload analysis."""
    contract_bytes = (
        b"Enterprise Cloud Service Level Agreement. "
        b"99.9% uptime commitment with standard 30-day termination notice. "
        b"Governed by Delaware state law."
    )

    if HAS_TESTCLIENT and client is not None:
        files = {
            "file": ("enterprise_agreement.txt", io.BytesIO(contract_bytes), "text/plain")
        }
        response = client.post("/api/v1/audit/file", files=files)
        assert response.status_code == 200
        report = response.json()
        assert report["file_name"] == "enterprise_agreement.txt"
        assert report["risk_tier"] == RiskTier.GREEN.value
        assert report["suspicion_score"] < 25
    else:
        upload = UploadFile(
            filename="enterprise_agreement.txt",
            file=io.BytesIO(contract_bytes),
        )
        report_obj = asyncio.run(audit_file(upload))
        assert report_obj.file_name == "enterprise_agreement.txt"
        assert report_obj.risk_tier == RiskTier.GREEN
        assert report_obj.suspicion_score < 25


def test_api_audit_file_empty_rejection() -> None:
    """Verifies defensive rejection on empty file upload."""
    if HAS_TESTCLIENT and client is not None:
        files = {
            "file": ("empty_contract.txt", io.BytesIO(b"   "), "text/plain")
        }
        response = client.post("/api/v1/audit/file", files=files)
        assert response.status_code == 422
    else:
        upload = UploadFile(
            filename="empty_contract.txt",
            file=io.BytesIO(b"   "),
        )
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(audit_file(upload))
        assert exc_info.value.status_code == 422