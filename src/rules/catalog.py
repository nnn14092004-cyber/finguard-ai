"""Regulatory Rule Catalog for FinGuard-AI.

Codifies heuristic regular expression rules mapping verbatim contractual clauses
to international financial frameworks (FATF, FCA, SEC Howey, FTC Koscot, Unfair Terms)
defined in the FinGuard Global Knowledge Base.
"""

from __future__ import annotations

import re
from typing import List
from src.domain.enums import RegulatoryFramework, RiskSeverity
from src.domain.models import RuleDefinition


class RegulatoryCatalog:
    """Centralized repository of codified regulatory violation definitions."""

    @classmethod
    def get_rules(cls) -> List[RuleDefinition]:
        """Returns the full deterministic heuristic rule collection with precompiled patterns."""
        return [
            # =========================================================================
            # 1. FATF / FCA HIGH-YIELD INVESTMENT FRAUD (HYIP)
            # =========================================================================
            RuleDefinition(
                rule_id="HYIP-001",
                rule_name="Unrealistic Guaranteed Periodic Yield",
                severity=RiskSeverity.TIER_1_CRITICAL,
                weight=40,
                category="Yield Guarantee",
                pattern=re.compile(
                    r"(?i)\b(?:guaranteed\s+(?:\d+(?:\.\d+)?%\s*(?:daily|per\s+day|monthly|per\s+month)|"
                    r"returns?|profits?|yields?|payouts?)|"
                    r"\d+(?:\.\d+)?%\s*(?:daily|per\s+day)\s+(?:roi|return|yield))\b"
                ),
                regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
                remediation_advice=(
                    "Under FATF and FCA standards, decoupling guaranteed returns from the sovereign risk-free "
                    "rate indicates High-Yield Investment Fraud (HYIP). Remove all absolute yield guarantees."
                ),
            ),
            RuleDefinition(
                rule_id="HYIP-002",
                rule_name="Unbacked Capital Protection & Zero-Risk Claim",
                severity=RiskSeverity.TIER_1_CRITICAL,
                weight=40,
                category="Risk Obfuscation",
                pattern=re.compile(
                    r"(?i)\b(?:100%\s+capital\s+guaranteed|zero[- ]risk\s+protocol|principal\s+protection\s+vault|"
                    r"complete\s+insulation\s+from\s+downside|guaranteed\s+capital\s+preservation)\b"
                ),
                regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
                remediation_advice=(
                    "Financial regulations prohibit marketing speculative algorithmic operations as zero-risk "
                    "or fully principal-protected without independent third-party regulatory escrow."
                ),
            ),
            RuleDefinition(
                rule_id="HYIP-003",
                rule_name="Artificial Scarcity & Coercive Urgency",
                severity=RiskSeverity.TIER_3_CAUTIONARY,
                weight=10,
                category="Psychological Coercion",
                pattern=re.compile(
                    r"(?i)\b(?:exclusive\s+founder\s+slots?|closing\s+in\s+\d+\s+hours?|"
                    r"limited\s+allocation\s+remaining|immediate\s+action\s+required\s+to\s+lock\s+in)\b"
                ),
                regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
                remediation_advice=(
                    "Eliminate high-pressure sales tactics and artificial scarcity triggers designed to bypass "
                    "statutory investor due diligence."
                ),
            ),
            # =========================================================================
            # 2. TECHNOLOGICAL OBFUSCATION (PONZI BUZZWORDS)
            # =========================================================================
            RuleDefinition(
                rule_id="TECH-001",
                rule_name="Technological Jargon Obfuscation",
                severity=RiskSeverity.TIER_2_HIGH,
                weight=20,
                category="Technological Obfuscation",
                pattern=re.compile(
                    r"(?i)\b(?:quantum\s+(?:arbitrage|vault)|ai\s+predictive(?:\s+high[- ]frequency)?\s+trading|"
                    r"defi\s+liquid\s+staking\s+yields?|autonomous\s+arbitrage|algorithmic\s+distribution\s+benchmark|"
                    r"vip\s+elite\s+wealth\s+system)\b"
                ),
                regulatory_framework=RegulatoryFramework.FATF_FCA_HYIP,
                remediation_advice=(
                    "Masking non-existent revenues behind speculative buzzwords without audited positive cash flow "
                    "is a recognized indicator of Ponzi architecture under IOSCO and OECD standards."
                ),
            ),
            # =========================================================================
            # 3. FTC / IOSCO PYRAMID & PONZI SCHEMES (KOSCOT DOCTRINE)
            # =========================================================================
            RuleDefinition(
                rule_id="PYR-001",
                rule_name="Multi-Tier Downline Recruitment Commission",
                severity=RiskSeverity.TIER_1_CRITICAL,
                weight=40,
                category="Pyramid Recruitment",
                pattern=re.compile(
                    r"(?i)\b(?:multi[- ]tier\s+(?:referral|downline|commission)|downline\s+investment\s+volume|"
                    r"generational\s+matching\s+bonus|referral\s+commission\s+structure|level\s+\d+\s+downlines?)\b"
                ),
                regulatory_framework=RegulatoryFramework.FTC_IOSCO_PYRAMID,
                remediation_advice=(
                    "Under FTC Koscot doctrine, compensating participants from downline capital recruitment "
                    "rather than bona fide retail commerce constitutes an unlawful pyramid scheme."
                ),
            ),
            RuleDefinition(
                rule_id="PYRAMID-001",
                rule_name="Multi-Tier Downline Recruitment Commission (Alias)",
                severity=RiskSeverity.TIER_1_CRITICAL,
                weight=0,
                category="Pyramid Recruitment",
                pattern=re.compile(
                    r"(?i)\b(?:multi[- ]tier\s+(?:referral|downline|commission)|downline\s+investment\s+volume|"
                    r"generational\s+matching\s+bonus|referral\s+commission\s+structure|level\s+\d+\s+downlines?)\b"
                ),
                regulatory_framework=RegulatoryFramework.FTC_IOSCO_PYRAMID,
                remediation_advice=(
                    "Under FTC Koscot doctrine, compensating participants from downline capital recruitment "
                    "rather than bona fide retail commerce constitutes an unlawful pyramid scheme."
                ),
            ),
            RuleDefinition(
                rule_id="PYR-002",
                rule_name="Binary Balancing Compensation Structure",
                severity=RiskSeverity.TIER_1_CRITICAL,
                weight=40,
                category="Pyramid Recruitment",
                pattern=re.compile(
                    r"(?i)\b(?:binary\s+(?:referral\s+)?bonus(?:es)?|binary\s+leg\s+balancing|"
                    r"weaker\s+leg\s+volume|binary\s+tree\s+compensation)\b"
                ),
                regulatory_framework=RegulatoryFramework.FTC_IOSCO_PYRAMID,
                remediation_advice=(
                    "Binary matrix balancing structures incentivizing capital pooling violate international "
                    "anti-pyramid statutes. Restructure compensation exclusively around retail sales."
                ),
            ),
            RuleDefinition(
                rule_id="PYRAMID-002",
                rule_name="Binary Balancing Compensation Structure (Alias)",
                severity=RiskSeverity.TIER_1_CRITICAL,
                weight=0,
                category="Pyramid Recruitment",
                pattern=re.compile(
                    r"(?i)\b(?:binary\s+(?:referral\s+)?bonus(?:es)?|binary\s+leg\s+balancing|"
                    r"weaker\s+leg\s+volume|binary\s+tree\s+compensation)\b"
                ),
                regulatory_framework=RegulatoryFramework.FTC_IOSCO_PYRAMID,
                remediation_advice=(
                    "Binary matrix balancing structures incentivizing capital pooling violate international "
                    "anti-pyramid statutes. Restructure compensation exclusively around retail sales."
                ),
            ),
            RuleDefinition(
                rule_id="PYRAMID-003",
                rule_name="Pay-to-Play Mandatory License/Package Requirement",
                severity=RiskSeverity.TIER_2_HIGH,
                weight=20,
                category="Pyramid Recruitment",
                pattern=re.compile(
                    r"(?i)\b(?:must\s+purchase\s+(?:an?\s+)?(?:ai\s+license|mining\s+node|starter\s+pack|membership\s+package)|"
                    r"mandatory\s+license\s+package\s+to\s+qualify|prerequisite\s+tier\s+purchase)\b"
                ),
                regulatory_framework=RegulatoryFramework.FTC_IOSCO_PYRAMID,
                remediation_advice=(
                    "Mandating upfront internal token, package, or license purchases as a condition to earn "
                    "returns is an illegal pyramid enrollment mechanism under FTC standards."
                ),
            ),
            # =========================================================================
            # 4. SEC HOWEY INVESTMENT CONTRACT STANDARD
            # =========================================================================
            RuleDefinition(
                rule_id="HOWEY-001",
                rule_name="SEC Howey Passive Investor Reliance",
                severity=RiskSeverity.TIER_1_CRITICAL,
                weight=40,
                category="Securities Classification",
                pattern=re.compile(
                    r"(?i)\b(?:solely\s+from\s+(?:the\s+)?efforts\s+of\s+others|"
                    r"executed\s+entirely\s+by\s+(?:our\s+)?algorithmic\s+team|"
                    r"remain\s+(?:completely\s+|entirely\s+)?passive|"
                    r"passive\s+(?:participants?|investors?|yield|income|returns?)|"
                    r"no\s+trading\s+expertise\s+required|"
                    r"syndicates?|yield\s+pooling|pooling\s+syndicate|"
                    r"collective\s+pooling(?:\s+vault)?|pooling\s+of\s+(?:investor\s+)?funds|"
                    r"passive\s+while\s+enjoying|capital\s+allocation\s+&\s+yield|"
                    r"investors\s+allocate\s+funds\s+into\s+our\s+capital\s+pool)\b"
                ),
                regulatory_framework=RegulatoryFramework.SEC_HOWEY_DOCTRINE,
                remediation_advice=(
                    "Deriving profits primarily from third-party algorithmic management with passive investor "
                    "reliance satisfies SEC Howey Prong 4. Requires registered prospectus or accredited exemption."
                ),
            ),
            # =========================================================================
            # 5. CROSS-BORDER UNFAIR CONTRACT TERMS & JURISDICTION LAUNDERING
            # =========================================================================
            RuleDefinition(
                rule_id="UNF-001",
                rule_name="Unilateral Discretionary Contract Modification",
                severity=RiskSeverity.TIER_2_HIGH,
                weight=20,
                category="Contractual Manipulation",
                pattern=re.compile(
                    r"(?i)\b(?:reserves?\s+the\s+right\s+to\s+(?:modify|amend|alter)\s+(?:terms|rates|rules|conditions)|"
                    r"without\s+prior\s+notice\s+at\s+its\s+sole\s+discretion|at\s+sole\s+discretion\s+without\s+notice)\b"
                ),
                regulatory_framework=RegulatoryFramework.UNFAIR_CONTRACT_TERMS,
                remediation_advice=(
                    "Unilateral terms modification without bilateral affirmative consent is void under "
                    "international consumer protection laws and unfair contract terms doctrines."
                ),
            ),
            RuleDefinition(
                rule_id="UNFAIR-001",
                rule_name="Unilateral Discretionary Contract Modification (Alias)",
                severity=RiskSeverity.TIER_2_HIGH,
                weight=0,
                category="Contractual Manipulation",
                pattern=re.compile(
                    r"(?i)\b(?:reserves?\s+the\s+right\s+to\s+(?:modify|amend|alter)\s+(?:terms|rates|rules|conditions)|"
                    r"without\s+prior\s+notice\s+at\s+its\s+sole\s+discretion|at\s+sole\s+discretion\s+without\s+notice)\b"
                ),
                regulatory_framework=RegulatoryFramework.UNFAIR_CONTRACT_TERMS,
                remediation_advice=(
                    "Unilateral terms modification without bilateral affirmative consent is void under "
                    "international consumer protection laws and unfair contract terms doctrines."
                ),
            ),
            RuleDefinition(
                rule_id="LOCK-001",
                rule_name="Mandatory Capital Lock-up Duration",
                severity=RiskSeverity.TIER_2_HIGH,
                weight=20,
                category="Liquidity Extortion",
                pattern=re.compile(
                    r"(?i)\b(?:mandatory\s+lock[- ]?up(?:\s+period)?(?:\s+of\s+\d+\s+months?)?|"
                    r"lock[- ]?up\s+(?:period\s+)?(?:of\s+)?\d+\s+months?|"
                    r"locked\s+(?:for\s+)?\d+\s+months?|\d+\s+months?\s+lock[- ]?up)\b"
                ),
                regulatory_framework=RegulatoryFramework.UNFAIR_CONTRACT_TERMS,
                remediation_advice=(
                    "Contractual capital lock-up intervals exceeding 12 months without emergency liquidity facilities "
                    "represent unconscionable liquidity entrapment."
                ),
            ),
            RuleDefinition(
                rule_id="LOCK-002",
                rule_name="Punitive Early Exit Penalty",
                severity=RiskSeverity.TIER_2_HIGH,
                weight=20,
                category="Liquidity Extortion",
                pattern=re.compile(
                    r"(?i)\b(?:early\s+withdrawal\s+(?:penalty|fee)|withdrawal\s+penalty|exit\s+penalty)"
                ),
                regulatory_framework=RegulatoryFramework.UNFAIR_CONTRACT_TERMS,
                remediation_advice=(
                    "Exit penalties stripping 30% or more of deposited principal are punitive and unenforceable "
                    "under statutory unfair contract terms legislation."
                ),
            ),
            RuleDefinition(
                rule_id="UNFAIR-003",
                rule_name="Conditioned Liquidity & Referral Quota Lock",
                severity=RiskSeverity.TIER_2_HIGH,
                weight=20,
                category="Liquidity Extortion",
                pattern=re.compile(
                    r"(?i)\b(?:withdrawals?\s+are\s+conditioned\s+upon\s+active\s+referrals?|"
                    r"withdrawal\s+eligibility\s+requires\s+(?:recruiting|network\s+volume)|"
                    r"must\s+maintain\s+active\s+referrals?\s+to\s+withdraw)\b"
                ),
                regulatory_framework=RegulatoryFramework.UNFAIR_CONTRACT_TERMS,
                remediation_advice=(
                    "Conditioning capital liquidity on recruiting downlines constitutes an extortionate predatory "
                    "mechanism and serves as definitive evidence of Ponzi collapse dynamics."
                ),
            ),
            RuleDefinition(
                rule_id="JUR-001",
                rule_name="Offshore Secrecy Jurisdiction Laundering",
                severity=RiskSeverity.TIER_3_CAUTIONARY,
                weight=10,
                category="Jurisdiction Laundering",
                pattern=re.compile(
                    r"(?i)\b(?:governed\s+by\s+the\s+laws\s+of\s+(?:seychelles|vanuatu|cayman(?:\s+islands)?|"
                    r"british\s+virgin\s+islands|bvi|marshall\s+islands|saint\s+vincent)|"
                    r"arbitration\s+in\s+(?:vanuatu|seychelles|cayman|bvi))\b"
                ),
                regulatory_framework=RegulatoryFramework.UNFAIR_CONTRACT_TERMS,
                remediation_advice=(
                    "Operating cross-border while specifying non-cooperative secrecy havens with cost-prohibitive "
                    "remote arbitration is a classic regulatory avoidance maneuver."
                ),
            ),
            RuleDefinition(
                rule_id="UNFAIR-004",
                rule_name="Offshore Secrecy Jurisdiction Laundering (Alias)",
                severity=RiskSeverity.TIER_3_CAUTIONARY,
                weight=0,
                category="Jurisdiction Laundering",
                pattern=re.compile(
                    r"(?i)\b(?:governed\s+by\s+the\s+laws\s+of\s+(?:seychelles|vanuatu|cayman(?:\s+islands)?|"
                    r"british\s+virgin\s+islands|bvi|marshall\s+islands|saint\s+vincent)|"
                    r"arbitration\s+in\s+(?:vanuatu|seychelles|cayman|bvi))\b"
                ),
                regulatory_framework=RegulatoryFramework.UNFAIR_CONTRACT_TERMS,
                remediation_advice=(
                    "Operating cross-border while specifying non-cooperative secrecy havens with cost-prohibitive "
                    "remote arbitration is a classic regulatory avoidance maneuver."
                ),
            ),
        ]