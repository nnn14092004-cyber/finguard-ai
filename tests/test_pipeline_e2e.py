"""End-to-End Integration Test Suite for FinGuard-AI Master Pipeline.

Verifies end-to-end audit contracts against FATF, FCA, SEC Howey, and FTC Koscot
standards defined in the global regulatory knowledge base.
"""

from __future__ import annotations

import pytest

from src.domain.enums import RegulatoryFramework, RiskTier
from src.pipeline import FinGuardPipeline


@pytest.fixture(scope="module")
def pipeline() -> FinGuardPipeline:
    """Fixture initializing the production pipeline instance."""
    return FinGuardPipeline()


class TestFinGuardPipelineE2E:
    """End-to-End regression tests for full contract auditing workflow."""

    def test_e2e_scam_contract_aura_neural_protocol(self, pipeline: FinGuardPipeline) -> None:
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

        # Mathematical score bounds assertions
        assert report.suspicion_score >= 75
        assert report.risk_tier == RiskTier.RED_FLAG
        assert report.total_findings >= 7

        # Multi-dimensional risk vector assertions
        assert report.risk_vector.yield_risk >= 70
        assert report.risk_vector.structural_risk >= 80
        assert report.risk_vector.liquidity_risk >= 50
        assert report.risk_vector.legal_risk >= 10

        # Semantic finding assertions
        semantic_topics = [item.clause_topic for item in report.semantic_findings]
        assert any("Basis Points" in topic for topic in semantic_topics)
        assert any("Downside" in topic for topic in semantic_topics)

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

        assert report.suspicion_score < 25
        assert report.risk_tier == RiskTier.GREEN
        assert report.scoring_breakdown.tier_1_critical_count == 0
        assert len(report.semantic_findings) == 0

    def test_e2e_howey_passive_reliance_detection(self, pipeline: FinGuardPipeline) -> None:
        """Verifies SEC Howey Test Prong 4 (Derived Solely from Efforts of Others)."""
        howey_text = (
            "Investors provide capital into our collective pooling vault. "
            "All trading strategies are executed entirely by our algorithmic team, "
            "allowing participants to remain completely passive while enjoying guaranteed profits."
        )
        report = pipeline.process_document(howey_text, file_name="howey_clause.txt")

        matching_frameworks = [
            f.regulatory_framework for f in report.findings
        ] + [
            s.regulatory_relevance for s in report.semantic_findings
        ]

        assert (
            RegulatoryFramework.HOWEY_TEST_SEC in matching_frameworks
            or RegulatoryFramework.SEC_HOWEY_DOCTRINE in matching_frameworks
            or RegulatoryFramework.SEC_HOWEY in matching_frameworks
            or any("passive" in f.matched_text.lower() for f in report.findings)
            or any("passive" in s.extracted_text.lower() for s in report.semantic_findings)
        )

    def test_e2e_empty_and_whitespace_input_resilience(
        self, pipeline: FinGuardPipeline
    ) -> None:
        """Verifies defensive handling of blank or whitespace input strings."""
        report = pipeline.process_document("   \n\t   ", file_name="empty.txt")
        assert report.suspicion_score == 0
        assert report.risk_tier == RiskTier.GREEN
        assert report.total_findings == 0
        assert len(report.semantic_findings) == 0