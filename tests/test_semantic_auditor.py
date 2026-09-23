"""Automated unit tests for the FinGuard-AI Contextual Semantic Auditor."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from src.domain.enums import Severity
from src.domain.models import DocumentPayload
from src.engines.semantic_auditor import SemanticAuditor


def test_semantic_auditor_handles_empty_input() -> None:
    """Verifies auditor gracefully returns empty findings for empty payloads."""
    auditor = SemanticAuditor()
    payload = DocumentPayload(raw_text="", normalized_text="")
    findings = auditor.audit(payload)
    assert findings == []


def test_semantic_auditor_fallback_detects_obfuscated_terms() -> None:
    """Verifies heuristic fallback catches sophisticated technological obfuscation."""
    auditor = SemanticAuditor()
    auditor.api_key = ""

    obfuscated_contract = (
        "Participants allocate digital liquidity to our autonomous neural arbitrage syndicate. "
        "Protocol consensus automatically redistributes generational yield proportional to network "
        "contribution without directional market dependency."
    )
    payload = DocumentPayload(raw_text=obfuscated_contract, normalized_text=obfuscated_contract)
    findings = auditor.audit(payload)

    assert len(findings) >= 2
    topics = [f.clause_topic for f in findings]
    assert "Algorithmic Yield Obfuscation" in topics
    assert "Disguised Pyramid Recruitment" in topics
    assert any(f.severity == Severity.CRITICAL for f in findings)


def test_semantic_auditor_parses_mocked_llm_json_response() -> None:
    """Verifies structured JSON mapping while eliminating network socket setup latency."""
    auditor = SemanticAuditor()
    auditor.api_key = "test_key_non_empty"

    mock_llm_response = [
        {
            "clause_topic": "Disguised Liquidity Lockup",
            "extracted_text": "Capital withdrawal requires protocol governance synchronization over 24 months.",
            "deceptive_intent": "Creates artificial barriers to exit under technical jargon.",
            "implicit_risk_level": "HIGH",
            "regulatory_relevance": "UNFAIR_TERMS",
            "penalty_weight": 20,
            "remediation_guidance": "Provide unconditional 30-day redemption windows.",
        }
    ]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(mock_llm_response)}]}}]
    }

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        payload = DocumentPayload(
            raw_text="Sample contract text for remote audit.",
            normalized_text="Sample contract text for remote audit.",
        )
        findings = auditor.audit(payload)

        assert len(findings) == 1
        finding = findings[0]
        assert finding.clause_topic == "Disguised Liquidity Lockup"
        assert finding.penalty_weight == 20
        assert finding.severity == Severity.HIGH
        assert finding.regulatory_relevance == "UNFAIR_TERMS"
