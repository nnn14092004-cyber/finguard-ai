"""Executable integration harness verifying the complete FinGuard-AI Phase 3 pipeline."""

from __future__ import annotations

from src.pipeline import FinGuardPipeline


def main() -> None:
    """Executes an end-to-end audit demonstrating hybrid heuristic and semantic detection."""
    synthetic_advanced_scam_contract = """
    AURA NEURAL PROTOCOL - PRIVATE PLACEMENT MEMORANDUM
    
    1. Capital Allocation & Yield Mechanics:
    Participants deposit capital into our autonomous liquidity allocation matrix.
    The protocol targets an algorithmic distribution benchmark yielding 150 basis points daily,
    backed by autonomous arbitrage with complete insulation from downside principal volatility.
    No trading expertise is required by passive participants.
    
    2. Affiliate Incentives & Tier Membership:
    Earn exceptional returns through our multi-tier referral commission structure.
    Receive downline investment volume bonuses and a binary bonus on newly recruited capital.
    Participants must purchase an AI license package to qualify for high-tier incentives.
    
    3. Liquidity & Capital Preservation:
    All allocated funds are subject to a mandatory lock-up period of 24 months.
    In the event of early liquidation, an early withdrawal penalty of 40% will be assessed.
    Withdrawals are conditioned upon maintaining active downline referral nodes.
    
    4. Governing Law & Arbitration:
    The issuer reserves the right to modify these terms, interest rates, and withdrawal rules
    at any time without prior notice.
    This agreement is strictly governed by the laws of Seychelles.
    All disputes shall be resolved solely via arbitration in Vanuatu.
    """

    print("=" * 80)
    print("FINGUARD-AI HYBRID ENTERPRISE AUDIT PIPELINE (PHASE 3: HEURISTIC + SEMANTIC)")
    print("=" * 80)

    pipeline = FinGuardPipeline()
    report = pipeline.process_document(
        raw_text=synthetic_advanced_scam_contract,
        file_name="aura_neural_protocol_ppm.txt",
    )

    print(f"Document ID       : {report.document_id}")
    print(f"File Name         : {report.file_name}")
    print(f"Suspicion Score   : {report.suspicion_score}/100")
    print(f"Risk Tier         : {report.risk_tier.value}")
    print(f"Total Violations  : {report.total_findings} (Heuristic: {len(report.findings)}, Semantic: {len(report.semantic_findings)})")

    print("\nMULTI-DIMENSIONAL RISK VECTOR:")
    print(f"  * Yield Deception Risk    [FATF/FCA] : {report.risk_vector.yield_risk}/100")
    print(f"  * Structural/Pyramid Risk [SEC/FTC]  : {report.risk_vector.structural_risk}/100")
    print(f"  * Liquidity Lockup Risk   [Unfair]   : {report.risk_vector.liquidity_risk}/100")
    print(f"  * Legal/Arbitration Risk  [Cross-B]  : {report.risk_vector.legal_risk}/100")

    print(f"\nExecutive Summary :\n{report.executive_summary}\n")

    if report.semantic_findings:
        print("SEMANTIC CONTEXTUAL FINDINGS (DEEP NLP AUDIT):")
        for idx, item in enumerate(report.semantic_findings, start=1):
            print(f"  [{idx}] {item.clause_topic} (Confidence: {item.confidence_score * 100:.1f}%)")
            print(f"      Matched Text : \"{item.extracted_text}\"")
            print(f"      Intent       : {item.deceptive_intent}")
            print(f"      Standard     : {item.regulatory_relevance.value}\n")

    print("DETERMINISTIC HEURISTIC FINDINGS:")
    for idx, item in enumerate(report.findings, start=1):
        print(f"  [{idx}] {item.rule_id} | {item.rule_name} (Weight: +{item.weight}) [{item.category}]")
        print(f"      Matched Quote : \"{item.matched_text}\"")
        print(f"      Remediation   : {item.remediation_advice}\n")

    print("ACTIONABLE REMEDIATION RECOMMENDATIONS:")
    for idx, action in enumerate(report.remediation_actions, start=1):
        print(f"  {idx}. {action}")
    print("=" * 80)


if __name__ == "__main__":
    main()