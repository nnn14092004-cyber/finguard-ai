"""Automated unit test suite verifying mathematical scoring, risk vectors, and tier mapping."""

from __future__ import annotations

import uuid

from src.domain.enums import RegulatoryFramework, RiskSeverity, RiskTier
from src.domain.models import ClauseFinding, DocumentPayload
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
    assert report.scoring_breakdown.raw_score == 0
    assert report.scoring_breakdown.capped_score == 0
    assert report.risk_vector.yield_risk == 0
    assert report.risk_vector.structural_risk == 0
    assert report.risk_vector.liquidity_risk == 0
    assert report.risk_vector.legal_risk == 0
    assert len(report.remediation_actions) == 1


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
        rule_name="Offshore Haven",
        severity=RiskSeverity.TIER_3_CAUTIONARY,
        weight=10,
        category="LEGAL",
        matched_text="Seychelles laws",
        start_index=20,
        end_index=35,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS_ACT,
        remediation_advice="Demand onshore jurisdiction.",
    )

    report_yellow = ScoringEngine.evaluate(payload, [finding_t2, finding_t3])
    assert report_yellow.suspicion_score == 30
    assert report_yellow.risk_tier == RiskTier.YELLOW
    assert report_yellow.risk_vector.liquidity_risk == 20
    assert report_yellow.risk_vector.legal_risk == 10
    assert report_yellow.risk_vector.yield_risk == 0
    assert report_yellow.risk_vector.structural_risk == 0

    finding_t1 = ClauseFinding(
        rule_id="HYIP-001",
        rule_name="Guaranteed Yield",
        severity=RiskSeverity.TIER_1_CRITICAL,
        weight=40,
        category="YIELD",
        matched_text="guaranteed 1% daily",
        start_index=0,
        end_index=19,
        regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
        remediation_advice="FATF Warning on HYIP.",
    )
    report_orange = ScoringEngine.evaluate(payload, [finding_t1, finding_t3])
    assert report_orange.suspicion_score == 50
    assert report_orange.risk_tier == RiskTier.ORANGE
    assert report_orange.risk_vector.yield_risk == 40
    assert report_orange.risk_vector.legal_risk == 10

    report_red = ScoringEngine.evaluate(payload, [finding_t1, finding_t1])
    assert report_red.suspicion_score == 80
    assert report_red.risk_tier == RiskTier.RED_FLAG
    assert report_red.risk_vector.yield_risk == 80


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

    excessive_findings = [critical_finding] * 4
    report = ScoringEngine.evaluate(payload, excessive_findings)

    assert report.scoring_breakdown.raw_score == 160
    assert report.scoring_breakdown.capped_score == 100
    assert report.suspicion_score == 100
    assert report.risk_tier == RiskTier.RED_FLAG
    assert report.risk_vector.yield_risk == 100


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
        rule_id="HYIP-002",
        rule_name="Monthly Yield",
        severity=RiskSeverity.TIER_1_CRITICAL,
        weight=40,
        category="YIELD",
        matched_text="guarantee 30% monthly",
        start_index=30,
        end_index=51,
        regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
        remediation_advice="Do not invest in fixed daily returns.",
    )

    report = ScoringEngine.evaluate(payload, [repeated_finding_a, repeated_finding_b])
    assert len(report.remediation_actions) == 1
    assert report.remediation_actions[0] == "Do not invest in fixed daily returns."