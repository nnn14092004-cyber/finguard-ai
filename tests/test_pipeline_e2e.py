"""End-to-End integration tests for FinGuard-AI compliance pipeline."""

from __future__ import annotations

import pytest
from src.domain.enums import RiskTier
from src.pipeline import FinGuardPipeline


@pytest.fixture
def pipeline() -> FinGuardPipeline:
    """Instantiates the master compliance audit pipeline."""
    return FinGuardPipeline()


class TestFinGuardPipelineE2E:
    """End-to-end integration test suite exercising the complete compliance workflow."""

    def test_e2e_scam_contract_aura_neural_protocol(
        self, pipeline: FinGuardPipeline
    ) -> None:
        """Verifies synthetic predatory contract triggers RED_FLAG tier and high risk vector."""
        malicious_contract = """
        AURA NEURAL PROTOCOL:
        Participants deposit capital into our autonomous liquidity allocation matrix.
        The protocol targets an algorithmic distribution benchmark yielding 150 basis points daily,
        backed by autonomous arbitrage with complete insulation from downside principal volatility.
        No trading expertise is required by passive participants.
        Earn returns through our multi-tier referral commission structure with downline investment
        volume bonuses and a binary bonus on newly recruited capital.
        Participants must purchase an AI license package to qualify.
        Mandatory lock-up period of 24 months applies with an early withdrawal penalty of 40%.
        Withdrawals are conditioned upon active referrals.
        Governed by the laws of Seychelles, arbitration in Vanuatu.
        """
        report = pipeline.process_document(malicious_contract, file_name="aura_protocol.txt")

        assert report.risk_tier == RiskTier.RED_FLAG
        assert report.suspicion_score >= 75
        assert report.risk_vector.yield_risk >= 50
        assert report.risk_vector.structural_risk >= 40
        assert report.risk_vector.liquidity_risk >= 50
        assert report.risk_vector.legal_risk >= 20
        assert len(report.findings) > 0

    def test_e2e_legitimate_enterprise_contract_green_tier(
        self, pipeline: FinGuardPipeline
    ) -> None:
        """Verifies legitimate enterprise cloud SLA receives GREEN tier (<25 points)."""
        legitimate_sla = """
        ENTERPRISE CLOUD SERVICE LEVEL AGREEMENT (SLA)
        1. Service Commitment: Provider guarantees 99.9% uptime for provisioned compute instances.
        2. Invoicing: Customer agrees to pay recurring monthly infrastructure service fees.
        3. Termination: Either party may terminate with 30 days prior written notice.
        4. Applicable Law: Governed by the laws of the State of Delaware, United States.
        """
        report = pipeline.process_document(legitimate_sla, file_name="cloud_sla.txt")

        assert report.risk_tier == RiskTier.GREEN
        assert report.suspicion_score < 25
        assert len(report.findings) == 0

    def test_e2e_howey_passive_reliance_detection(
        self, pipeline: FinGuardPipeline
    ) -> None:
        """Verifies SEC Howey Test Prong 4 (Derived Solely from Efforts of Others)."""
        howey_text = (
            "Investors provide capital into our collective pooling vault. "
            "All trading strategies are executed entirely by our algorithmic team, "
            "allowing participants to remain completely passive while enjoying guaranteed profits."
        )
        report = pipeline.process_document(howey_text, file_name="howey_clause.txt")

        assert report.suspicion_score >= 40
        assert report.risk_vector.structural_risk >= 40
        rule_ids = {f.rule_id for f in report.findings}
        assert "HOWEY-001" in rule_ids

    def test_e2e_empty_and_whitespace_input_resilience(
        self, pipeline: FinGuardPipeline
    ) -> None:
        """Verifies defensive handling of blank or whitespace input strings."""
        report = pipeline.process_document("   \n\t   ", file_name="empty.txt")

        assert report.suspicion_score == 0
        assert report.risk_tier == RiskTier.GREEN
        assert report.total_findings == 0