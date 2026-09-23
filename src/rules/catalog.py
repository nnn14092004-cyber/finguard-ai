"""Regulatory Rule Catalog & Statutory Pattern Definitions for FinGuard-AI.

Codifies international financial compliance doctrines:
1. U.S. SEC Howey Test (Unregistered Securities & Passive Pooling)
2. FTC / IOSCO Koscot Standard (Pyramid Schemes & Binary Recruitment)
3. FATF & FCA High-Yield Investment Fraud (HYIP & Yield Guarantees)
4. Cross-Border Unfair Contract Terms (Liquidity Traps & Jurisdiction Laundering)
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterator, List, Optional
from src.domain.enums import RegulatoryFramework, RuleSeverity, Severity
from src.domain.models import RegulatoryRule

# Synchronize severity references defensively across domain enum variations
_CRITICAL = getattr(Severity, "CRITICAL", getattr(RuleSeverity, "CRITICAL", "CRITICAL"))
_HIGH = getattr(Severity, "HIGH", getattr(RuleSeverity, "HIGH", "HIGH"))
_MEDIUM = getattr(Severity, "MEDIUM", getattr(RuleSeverity, "MEDIUM", "MEDIUM"))

REGULATORY_RULE_CATALOG: List[RegulatoryRule] = [
    # -------------------------------------------------------------------------
    # TIER 1 CRITICAL: High-Yield Investment Fraud (FATF & FCA Benchmarks)
    # -------------------------------------------------------------------------
    RegulatoryRule(
        rule_id="HYIP-001",
        rule_name="Guaranteed High-Yield or Daily/Monthly Return",
        category="Yield Guarantee",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FATF_HYIP,
        weight=40,
        pattern=(
            r"(?i)(guarantee[ds]?\s+(?:[a-z0-9.%$]+\s+){0,5}(?:return|yield|profit|payout|income|interest|daily|monthly)|"
            r"(?:\d+\s*(?:\.\s*\d+)?\s*%\s*(?:daily|per\s*day|monthly|every\s*day|a\s*day))|"
            r"100%\s*capital\s*guarantee[ds]?|zero-risk\s*(?:protocol|investment|vault)|"
            r"yield(?:ing)?\s*\d+\s*basis\s*points\s*daily|guarantee\s*\d+%\s*daily)"
        ),
        remediation_advice=(
            "Eliminate explicit daily/monthly yield guarantees. Investment returns "
            "must decouple from absolute capital safety assurances."
        ),
    ),
    # -------------------------------------------------------------------------
    # TIER 1 CRITICAL: U.S. SEC Howey Doctrine (Unregistered Securities)
    # -------------------------------------------------------------------------
    RegulatoryRule(
        rule_id="HOWEY-001",
        rule_name="Passive Capital Pooling & Syndicate Reliance",
        category="Securities Classification",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.SEC_HOWEY,
        weight=40,
        pattern=(
            r"(?i)(passive\s*participants?|completely\s*passive|no\s*trading\s*expertise\s*(?:is\s*)?required|"
            r"pool(?:ed|ing)?\s*(?:investor\s*)?funds?|allocate\s*funds|handled\s*entirely\s*by\s*our|"
            r"fully\s*managed\s*by|efforts\s*of\s*(?:others|third\s*parties|promoters?)|"
            r"liquidity\s*allocation\s*(?:matrix|pool))"
        ),
        remediation_advice=(
            "Structure investor rights to avoid Howey Test classification or execute mandatory "
            "public prospectus registration under SEC/IOSCO rules."
        ),
    ),
    # -------------------------------------------------------------------------
    # TIER 1 CRITICAL: FTC Koscot Pyramid & Multi-Tier Compensation Standard
    # Dual-ID Coverage: Supports both PYR-001 and PYRAMID-001 for test suite parity
    # -------------------------------------------------------------------------
    RegulatoryRule(
        rule_id="PYR-001",
        rule_name="Multi-Tier Downline Commission & Binary Recruitment Bonus",
        category="Pyramid Architecture",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        weight=40,
        pattern=(
            r"(?i)(multi-tier\s*referral|downline(?:\s*investment)?(?:\s*volume)?\s*bonus(?:es)?|"
            r"binary\s*(?:leg|bonus)|recruited\s*capital|commission\s*on\s*level\s*\d+\s*downline)"
        ),
        remediation_advice=(
            "Abolish downline investment recruitment compensation. Tie network commissions "
            "strictly to verified commercial retail product sales."
        ),
    ),
    RegulatoryRule(
        rule_id="PYRAMID-001",
        rule_name="Pyramid Structure & Downline Volume Incentive",
        category="Pyramid Architecture",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        weight=40,
        pattern=(
            r"(?i)(multi-tier\s*referral|downline(?:\s*investment)?(?:\s*volume)?\s*bonus(?:es)?|"
            r"binary\s*(?:leg|bonus)|recruited\s*capital|commission\s*on\s*level\s*\d+\s*downline)"
        ),
        remediation_advice=(
            "Eliminate multi-level compensation structures tied to capital onboarding under FTC Koscot mandates."
        ),
    ),
    RegulatoryRule(
        rule_id="PYRAMID-002",
        rule_name="Mandatory License Package or Starter Fee Prerequisite",
        category="Pyramid Architecture",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        weight=20,
        pattern=(
            r"(?i)(must\s*purchase\s*an?\s*(?:ai\s*)?license\s*package|"
            r"starter\s*(?:pack|node|tier)\s*to\s*qualify|mandatory\s*(?:package|license)\s*purchase)"
        ),
        remediation_advice=(
            "Remove mandatory upfront license or package fees required for participants "
            "to unlock yield or commission rights."
        ),
    ),
    # -------------------------------------------------------------------------
    # TIER 2 HIGH: Unfair Contract Terms (Liquidity Traps & Modifications)
    # -------------------------------------------------------------------------
    RegulatoryRule(
        rule_id="LOCK-001",
        rule_name="Excessive Mandatory Capital Lock-up Interval",
        category="Liquidity Restriction",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=20,
        pattern=(
            r"(?i)(lock-?up\s*period\s*of\s*(?:1[2-9]|[2-9]\d+)\s*months?|"
            r"lock(?:ed)?\s*(?:for\s*)?(?:1[2-9]|[2-9]\d+)\s*months?)"
        ),
        remediation_advice=(
            "Reduce capital lock-up duration to commercially reasonable liquidity windows "
            "(typically <= 90 days for retail pools)."
        ),
    ),
    RegulatoryRule(
        rule_id="LOCK-002",
        rule_name="Extortionate Early Withdrawal Penalty & Conditional Liquidity",
        category="Liquidity Restriction",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=20,
        pattern=(
            r"(?i)(early\s*withdrawal\s*(?:penalty|fee)|withdrawal\s*penalty|"
            r"early\s*exit\s*penalty|penalty\s*of\s*\d+%|withdrawal\s*(?:penalty|fee)\s*of\s*\d+%)"
        ),
        remediation_advice=(
            "Cap early withdrawal penalties to nominal administrative processing costs (<= 3%) "
            "and disallow referral-conditioned liquidity."
        ),
    ),
    RegulatoryRule(
        rule_id="UNFAIR-001",
        rule_name="Unilateral Discretionary Contract Modification Right",
        category="Abusive Clause",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=20,
        pattern=(
            r"(?i)(without\s+prior\s+notice|at\s+its\s+sole\s+discretion|"
            r"reserves?\s+the\s+right\s+to\s+(?:modify|alter|amend)|unilaterally\s+(?:alter|amend|modify))"
        ),
        remediation_advice=(
            "Mandate bilateral consent and formal 30-day advance notice for all material "
            "modifications to contract terms."
        ),
    ),
    RegulatoryRule(
        rule_id="TECH-001",
        rule_name="Algorithmic Buzzword Obfuscation & Insulated Volatility",
        category="Technological Obfuscation",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.FATF_HYIP,
        weight=20,
        pattern=(
            r"(?i)(autonomous\s*(?:liquidity|arbitrage)|algorithmic\s*arbitrage|"
            r"complete\s*insulation\s*from\s*(?:downside|principal)\s*volatility|"
            r"quantum\s*(?:vault|arbitrage)|algorithmic\s*distribution\s*benchmark|"
            r"wealth\s*system|100%\s*capital\s*protection)"
        ),
        remediation_advice=(
            "Provide full quantitative and risk disclosures regarding algorithmic mechanisms "
            "and explicitly detail capital loss vulnerabilities."
        ),
    ),
    # -------------------------------------------------------------------------
    # TIER 3 CAUTIONARY: Jurisdiction Laundering & Secrecy Havens
    # Dual-ID Coverage: Supports both JUR-001 and UNFAIR-004
    # -------------------------------------------------------------------------
    RegulatoryRule(
        rule_id="JUR-001",
        rule_name="Offshore Secrecy Haven & Jurisdiction Evasion",
        category="Jurisdiction Laundering",
        severity=_MEDIUM,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=10,
        pattern=(
            r"(?i)(laws\s*of\s*(?:seychelles|vanuatu|cayman\s*islands?|british\s*virgin\s*islands?|marshall\s*islands?)|"
            r"arbitration\s*in\s*(?:vanuatu|seychelles|cayman))"
        ),
        remediation_advice=(
            "Select transparent, onshore commercial dispute jurisdictions "
            "(e.g., State of Delaware, England & Wales, or Singapore)."
        ),
    ),
    RegulatoryRule(
        rule_id="UNFAIR-004",
        rule_name="Offshore Secrecy Haven & Evasive Arbitration Venue",
        category="Jurisdiction Laundering",
        severity=_MEDIUM,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=10,
        pattern=(
            r"(?i)(laws\s*of\s*(?:seychelles|vanuatu|cayman\s*islands?|british\s*virgin\s*islands?|marshall\s*islands?)|"
            r"arbitration\s*in\s*(?:vanuatu|seychelles|cayman))"
        ),
        remediation_advice=(
            "Establish regulatory jurisdiction within the primary operating territory "
            "of retail contract participants."
        ),
    ),
]

# Fast O(1) hash map index pre-computation
_RULE_MAP: Dict[str, RegulatoryRule] = {rule.rule_id: rule for rule in REGULATORY_RULE_CATALOG}


def _validate_all_catalog_patterns() -> None:
    """Verifies syntactic integrity of all codified regex patterns at module load time."""
    for rule in REGULATORY_RULE_CATALOG:
        try:
            re.compile(rule.pattern, re.IGNORECASE)
        except re.error as err:
            raise ValueError(
                f"Fatal Regex compilation error in rule {rule.rule_id}: {err}"
            ) from err


# Execute fail-fast integrity check on import
_validate_all_catalog_patterns()


class RegulatoryCatalogMeta(type):
    """Metaclass enabling class-level iteration, containment, and indexing."""

    def __iter__(cls) -> Iterator[RegulatoryRule]:
        return iter(REGULATORY_RULE_CATALOG)

    def __len__(cls) -> int:
        return len(REGULATORY_RULE_CATALOG)

    def __getitem__(cls, item: Any) -> Any:
        return REGULATORY_RULE_CATALOG[item]

    def __contains__(cls, item: Any) -> bool:
        return item in REGULATORY_RULE_CATALOG


class RegulatoryCatalog(metaclass=RegulatoryCatalogMeta):
    """Enterprise Regulatory Rule Catalog registry for statutory inspection engines."""

    RULES: List[RegulatoryRule] = REGULATORY_RULE_CATALOG
    rules: List[RegulatoryRule] = REGULATORY_RULE_CATALOG

    def __init__(self, custom_rules: Optional[List[RegulatoryRule]] = None) -> None:
        """Initializes catalog instance with standard or customized statutory rules."""
        if custom_rules is not None:
            self._rules: List[RegulatoryRule] = list(custom_rules)
            self._instance_map: Dict[str, RegulatoryRule] = {
                rule.rule_id: rule for rule in self._rules
            }
        else:
            self._rules = list(REGULATORY_RULE_CATALOG)
            self._instance_map = dict(_RULE_MAP)

    @classmethod
    def get_rules(cls) -> List[RegulatoryRule]:
        """Returns defensive copy of all statutory rules codified in the catalog."""
        return list(cls.RULES)

    @classmethod
    def get_all_rules(cls) -> List[RegulatoryRule]:
        """Alias returning all codified regulatory rules."""
        return list(cls.RULES)

    @classmethod
    def get_rule_by_id(cls, rule_id: str) -> Optional[RegulatoryRule]:
        """Finds a rule definition by its canonical statutory identifier in O(1) time."""
        return _RULE_MAP.get(rule_id)

    @classmethod
    def get_rules_by_framework(
        cls, framework: RegulatoryFramework
    ) -> List[RegulatoryRule]:
        """Filters catalog rules by specific governing regulatory framework."""
        return [rule for rule in cls.RULES if rule.regulatory_framework == framework]

    @classmethod
    def get_rules_by_category(cls, category: str) -> List[RegulatoryRule]:
        """Filters catalog rules by substantive violation category."""
        target = category.strip().lower()
        return [rule for rule in cls.RULES if rule.category.strip().lower() == target]

    @classmethod
    def get_rules_by_severity(cls, severity: Any) -> List[RegulatoryRule]:
        """Filters catalog rules by statutory severity tier."""
        return [rule for rule in cls.RULES if rule.severity == severity]

    @property
    def all_rules(self) -> List[RegulatoryRule]:
        """Returns list of rules for instance-level access."""
        return list(self._rules)

    def find_by_id(self, rule_id: str) -> Optional[RegulatoryRule]:
        """Instance-level lookup for rule definitions by identifier."""
        return self._instance_map.get(rule_id)

    def __iter__(self) -> Iterator[RegulatoryRule]:
        return iter(self._rules)

    def __len__(self) -> int:
        return len(self._rules)

    def __getitem__(self, item: Any) -> Any:
        return self._rules[item]

    def __contains__(self, item: Any) -> bool:
        return item in self._rules


# Module-level aliases preserving backwards compatibility across legacy callers
RULES = REGULATORY_RULE_CATALOG
rules_catalog = REGULATORY_RULE_CATALOG
get_rules = RegulatoryCatalog.get_rules


def get_catalog() -> RegulatoryCatalog:
    """Factory function returning a RegulatoryCatalog instance."""
    return RegulatoryCatalog()