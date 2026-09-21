"""Automated Batch Regulatory Auditing Harness for FinGuard-AI.

Scans synthetic and real-world financial agreements across regulatory benchmarks
(FATF, FCA, SEC Howey, FTC Koscot, Unfair Contract Terms), calculates multi-dimensional
risk vectors, outputs a tabular terminal matrix, and exports serialized JSON audit artifacts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure repository root is discoverable in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.domain.enums import RiskTier
from src.pipeline import FinGuardPipeline


def run_batch_regulatory_audit() -> None:
    """Executes multi-document compliance auditing across test corpus."""
    pipeline = FinGuardPipeline()

    synthetic_corpus: Dict[str, str] = {
        "Aura_Neural_Protocol_PPM.txt": (
            "AURA NEURAL PROTOCOL - CONFIDENTIAL OFFERING MEMORANDUM\n"
            "1. Capital Deployment & Target Yield:\n"
            "Participants deposit digital assets into our autonomous algorithmic liquidity allocation matrix. "
            "The protocol targets an algorithmic distribution benchmark yielding 150 basis points daily, "
            "backed by autonomous arbitrage with complete insulation from downside principal volatility.\n"
            "2. Passive Participation & Management:\n"
            "No trading expertise is required by passive participants. All execution is handled entirely "
            "by our specialized quantitative algorithmic team.\n"
            "3. Network Incentives & Multi-Tier Compensation:\n"
            "Participants earn revenue through our multi-tier referral commission structure with downline investment "
            "volume bonuses and a binary bonus on newly recruited capital. Participants must purchase an AI license package to qualify.\n"
            "4. Liquidity Terms & Jurisdiction:\n"
            "Mandatory lock-up period of 24 months applies with an early withdrawal penalty of 40%. "
            "Withdrawals are conditioned upon maintaining active referrals. "
            "This instrument is governed by the laws of Seychelles, with mandatory confidential arbitration in Vanuatu."
        ),
        "Alpha_Yield_Staking_Vault.txt": (
            "ALPHA YIELD AUTOMATED VAULT TERMS:\n"
            "Deposit funds for guaranteed 2.0% daily compounding returns. 100% capital guaranteed with zero-risk protocol. "
            "Earn 15% direct commission on level 1 downlines and 5% on level 2 downlines. "
            "The company reserves the right to modify terms and withdrawal limits at its sole discretion without prior notice. "
            "Governed by the laws of Cayman Islands."
        ),
        "Nexus_Advisory_Cautionary_Note.txt": (
            "NEXUS STRATEGIC ADVISORY RETAINER AGREEMENT:\n"
            "Client engages advisor for algorithmic execution consulting. Advisor provides periodic strategy reports. "
            "Consulting fees are billed monthly at standard commercial rates. "
            "Lock-up period of 14 months applies to strategy licensing. "
            "Governed by the commercial laws of the British Virgin Islands."
        ),
        "SafeCloud_Enterprise_SLA.txt": (
            "ENTERPRISE CLOUD SERVICE LEVEL AGREEMENT (SLA)\n"
            "1. Service Commitment: Provider guarantees 99.9% uptime for provisioned compute infrastructure.\n"
            "2. Invoicing & Fees: Customer agrees to pay recurring monthly infrastructure service charges.\n"
            "3. Termination: Either party may terminate the agreement with 30 days prior written notice.\n"
            "4. Applicable Jurisdiction: Governed by the laws of the State of Delaware, United States."
        ),
    }

    print("=" * 105)
    print("FINGUARD-AI ENTERPRISE BATCH REGULATORY AUDITING HARNESS")
    print("=" * 105)
    print(
        f"{'Document Identifier':<35} | {'Score':<6} | {'Tier':<10} | {'Findings':<9} | "
        f"{'Yield':<6} | {'Struct':<6} | {'Liq':<6} | {'Legal':<6}"
    )
    print("-" * 105)

    audit_records: List[Dict[str, Any]] = []

    for doc_name, content in synthetic_corpus.items():
        report = pipeline.process_document(raw_text=content, file_name=doc_name)

        v = report.risk_vector
        print(
            f"{doc_name:<35} | "
            f"{report.suspicion_score:<6} | "
            f"{report.risk_tier.value:<10} | "
            f"{report.total_findings:<9} | "
            f"{v.yield_risk:<6} | "
            f"{v.structural_risk:<6} | "
            f"{v.liquidity_risk:<6} | "
            f"{v.legal_risk:<6}"
        )

        audit_records.append(
            {
                "document_id": report.document_id,
                "file_name": doc_name,
                "suspicion_score": report.suspicion_score,
                "risk_tier": report.risk_tier.value,
                "risk_vector": report.risk_vector.model_dump(),
                "total_findings": report.total_findings,
                "heuristic_finding_count": len(report.findings),
                "semantic_finding_count": len(report.semantic_findings),
                "executive_summary": report.executive_summary,
                "remediation_actions": report.remediation_actions,
            }
        )

    print("=" * 105)

    output_path = ROOT_DIR / "batch_audit_summary.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_records, f, indent=2)

    print(f"\n[+] Batch compliance audit successfully executed.")
    print(f"[+] Serialized JSON report generated at: {output_path.resolve()}\n")


if __name__ == "__main__":
    run_batch_regulatory_audit()