"""Unit tests for the FinGuard-AI Mathematical Risk Scoring Engine."""

from __future__ import annotations

import uuid
import pytest
from src.domain.enums import RegulatoryFramework, RiskSeverity, RiskTier, Severity
from src.domain.models import ClauseFinding, DocumentPayload, Finding
from src.engines.scoring_engine import ScoringEngine


def _create_mock_payload() -> DocumentPayload:
    """Generates an immutable document container for isolated mathematical scoring tests."""
    return DocumentPayload(
        document_id=str(uuid.uuid4()),
        file_name="mock_instrument.txt",
        raw_content="Benchmark testing text payload",
        normalized_content="Benchmark testing text payload",
        character_count=31,
    )


def test_scoring_engine_zero_findings_yields_green_tier() -> None:
    """Verifies that a clean document receives zero penalty and GREEN tier."""
    payload = _create_mock_payload()
    report = ScoringEngine.evaluate(payload, findings=[])

    assert report.suspicion_score == 0
    assert report.risk_tier == RiskTier.GREEN
    assert report.total_findings == 0
    assert len(report.remediation_actions) > 0


def test_scoring_engine_tier_classification_and_risk_vector() -> None:
    """Verifies accurate categorization across thresholds and decomposed vector sub-scores."""
    payload = _create_mock_payload()

    finding_t2 = ClauseFinding(
        rule_id="LOCK-001",
        rule_name="Lockup",
        severity=RiskSeverity.TIER_2_HIGH,
        weight=20,
        category="LIQUIDITY",
        matched_text="locked 18 months",
        start_index=0,
        end_index=16,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS_ACT,
        remediation_advice="Review lockup provisions.",
    )

    finding_t3 = ClauseFinding(
        rule_id="JUR-001",
        rule_name="Offshore Jurisdiction",
        severity=RiskSeverity.TIER_3_CAUTIONARY,
        weight=10,
        category="JURISDICTION",
        matched_text="governed by Vanuatu",
        start_index=20,
        end_index=39,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS_ACT,
        remediation_advice="Select onshore commercial dispute jurisdictions.",
    )

    report = ScoringEngine.evaluate(payload, findings=[finding_t2, finding_t3])

    assert report.suspicion_score == 30
    assert report.risk_tier == RiskTier.YELLOW
    assert report.risk_vector.liquidity_risk > 0
    assert report.risk_vector.legal_risk > 0


def test_scoring_engine_caps_at_maximum_one_hundred() -> None:
    """Verifies that mathematical formula S = min(100, sum) strictly prevents scores over 100."""
    payload = _create_mock_payload()

    critical_finding = ClauseFinding(
        rule_id="HYIP-001",
        rule_name="Guaranteed Yield",
        severity=RiskSeverity.TIER_1_CRITICAL,
        weight=40,
        category="YIELD",
        matched_text="guaranteed 2% daily",
        start_index=0,
        end_index=19,
        regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
        remediation_advice="FATF Warning on HYIP.",
    )
    howey_finding = ClauseFinding(
        rule_id="HOWEY-001",
        rule_name="Passive Pooling",
        severity=RiskSeverity.TIER_1_CRITICAL,
        weight=40,
        category="HOWEY",
        matched_text="pooled capital",
        start_index=20,
        end_index=34,
        regulatory_framework=RegulatoryFramework.SEC_HOWEY,
        remediation_advice="Securities registration required.",
    )
    pyramid_finding = ClauseFinding(
        rule_id="PYR-001",
        rule_name="Binary MLM",
        severity=RiskSeverity.TIER_1_CRITICAL,
        weight=40,
        category="PYRAMID",
        matched_text="binary bonus",
        start_index=35,
        end_index=47,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        remediation_advice="FTC Koscot violation.",
    )

    report = ScoringEngine.evaluate(
        payload, findings=[critical_finding, howey_finding, pyramid_finding]
    )

    assert report.suspicion_score == 100
    assert report.risk_tier == RiskTier.RED_FLAG


def test_scoring_engine_deduplicates_remediation_actions() -> None:
    """Verifies that duplicated identical remediation advice strings are collapsed."""
    payload = _create_mock_payload()

    repeated_finding_a = ClauseFinding(
        rule_id="HYIP-001",
        rule_name="Daily Yield",
        severity=RiskSeverity.TIER_1_CRITICAL,
        weight=40,
        category="YIELD",
        matched_text="guarantee 1% daily",
        start_index=0,
        end_index=18,
        regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
        remediation_advice="Do not invest in fixed daily returns.",
    )
    repeated_finding_b = ClauseFinding(
        rule_id="HYIP-001",
        rule_name="Daily Yield Duplicate",
        severity=RiskSeverity.TIER_1_CRITICAL,
        weight=40,
        category="YIELD",
        matched_text="guarantee 2% daily",
        start_index=20,
        end_index=38,
        regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
        remediation_advice="Do not invest in fixed daily returns.",
    )

    report = ScoringEngine.evaluate(
        payload, findings=[repeated_finding_a, repeated_finding_b]
    )

    assert report.remediation_actions.count("Do not invest in fixed daily returns.") == 1