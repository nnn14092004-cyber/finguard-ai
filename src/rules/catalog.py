"""Statutory regulatory rule catalog codifying international compliance benchmarks."""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from src.domain.enums import RegulatoryFramework, RuleSeverity, Severity
from src.domain.models import RegulatoryRule

_CRITICAL = getattr(Severity, "CRITICAL", getattr(RuleSeverity, "CRITICAL", "CRITICAL"))
_HIGH = getattr(Severity, "HIGH", getattr(RuleSeverity, "HIGH", "HIGH"))
_MEDIUM = getattr(Severity, "MEDIUM", getattr(RuleSeverity, "MEDIUM", "MEDIUM"))

REGULATORY_RULE_CATALOG: list[RegulatoryRule] = [
    # Tier 1 Critical: High-yield promises and capital guarantees (FATF/FCA)
    RegulatoryRule(
        rule_id="HYIP-001",
        rule_name="Guaranteed High-Yield Velocity Assertion",
        category="Yield Guarantee",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FATF_HYIP,
        weight=40,
        patterns=[
            r"(?i)\bguarantee[ds]?\s+(?:[a-z0-9.%$]+\s+){0,5}(?:return|yield|profit|payout|income|interest|daily|monthly)\b",
            r"(?i)\b(?:\d+\s*(?:\.\s*\d+)?\s*%\s*(?:daily|per\s*day|monthly|every\s*day|a\s*day))\b",
            r"(?i)\b100%\s*capital\s*guarantee[ds]?\b",
            r"(?i)\bzero-risk\s*(?:protocol|investment|vault)\b",
            r"(?i)\byield(?:ing)?\s*\d+\s*basis\s*points\s*daily\b",
            r"(?i)\bguarantee\s*\d+%\s*daily\b",
            r"(?i)\bfixed\s+daily\s+return\b",
        ],
        remediation_advice=(
            "Eliminate all explicit daily or monthly return assertions. Investment returns "
            "must decouple from absolute capital safety assurances under FATF standards."
        ),
    ),
    # Tier 1 Critical: SEC Howey test securities classification
    RegulatoryRule(
        rule_id="HOWEY-001",
        rule_name="Passive Capital Pooling & Third-Party Managerial Reliance",
        category="Securities Classification",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.SEC_HOWEY,
        weight=40,
        patterns=[
            r"(?i)\bpassive\s*(?:participants?|investors?|income|dividends?|yield|returns?)\b",
            r"(?i)\bcompletely\s+passive\b",
            r"(?i)\bno\s*trading\s*expertise\s*(?:is\s*)?required\b",
            r"(?i)\bpool(?:ed|ing)?\s*(?:of\s*)?(?:investor\s*)?(?:funds?|capital)\b",
            r"(?i)\b(?:allocate|allocating)\s*(?:digital\s*)?(?:funds?|capital|liquidity)\b",
            r"(?i)\bhandled\s*entirely\s*by\s*our\b",
            r"(?i)\bfully\s*managed\s*by\b",
            r"(?i)\befforts\s*of\s*(?:others|third\s*parties|promoters?|management)\b",
            r"(?i)\bderived\s*(?:solely\s*)?from\s*(?:the\s*)?efforts\s*of\b",
            r"(?i)\bliquidity\s*allocation\s*(?:matrix|pool)\b",
            r"(?i)\bcommon\s*enterprise\b",
        ],
        remediation_advice=(
            "Structure investor rights to avoid Howey Test classification or execute mandatory "
            "public prospectus registration under SEC and IOSCO frameworks."
        ),
    ),
    # Tier 1 Critical: FTC Koscot pyramid scheme architecture
    RegulatoryRule(
        rule_id="MLM-001",
        rule_name="Multi-Tier Downline Capital Referral Commissions",
        category="Pyramid Architecture",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        weight=40,
        patterns=[
            r"(?i)\bmulti-tier\s*(?:referral|affiliate|downline|commission)\b",
            r"(?i)\bdownline(?:\s*investment)?(?:\s*volume)?\s*bonus(?:es)?\b",
            r"(?i)\bmatching\s*(?:downline\s*)?referral\s*bonus\b",
            r"(?i)\bbinary\s*(?:legs?|bonus|tree|matrix)\b",
            r"(?i)\bcommission\s*on\s*level\s*\d+\s*downline\b",
            r"(?i)\bmatching\s*bonus\s*across\s*(?:binary\s*legs|\d+\s*generations?)\b",
            r"(?i)\brecruited\s*capital\b",
            r"(?i)\bgenerations?\s*(?:commission|matching\s*bonus)\b",
        ],
        remediation_advice=(
            "Abolish capital onboarding incentives under FTC Koscot mandates. Network compensations "
            "must tie exclusively to verified commercial end-user retail product transactions."
        ),
    ),
    RegulatoryRule(
        rule_id="PYRAMID-001",
        rule_name="Downline Investment Volume Recruitment Incentive",
        category="Pyramid Architecture",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        weight=40,
        patterns=[
            r"(?i)\brecruited\s*capital\s*incentive\b",
            r"(?i)\bcommission\s*derived\s*from\s*investor\s*deposits\b",
            r"(?i)\bdownline\s*capital\s*generation\b",
            r"(?i)\bdownline(?:\s*investment)?(?:\s*volume)?\s*bonus(?:es)?\b",
        ],
        remediation_advice="Decouple all participant compensation from downstream deposit volumes.",
    ),
    RegulatoryRule(
        rule_id="PYR-001",
        rule_name="Multi-Tier Recruitment Structure Alias",
        category="Pyramid Architecture",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        weight=40,
        patterns=[
            r"(?i)\bmulti-tier\s*referral\b",
            r"(?i)\bbinary\s*leg\s*balancing\b",
            r"(?i)\bdownline\s*investment\s*volume\b",
        ],
        remediation_advice="Eliminate multi-level compensation structures tied to capital onboarding.",
    ),
    # Tier 1 Critical: FATF Travel Rule circumvention and unhosted wallets
    RegulatoryRule(
        rule_id="AML-001",
        rule_name="Mandatory Unhosted Wallet Routing & AML Circumvention",
        category="AML Evasion",
        severity=_CRITICAL,
        regulatory_framework=RegulatoryFramework.FATF_HYIP,
        weight=40,
        patterns=[
            r"(?i)\bdeposit\s*to\s*(?:anonymous|unhosted|personal)\s*(?:crypto\s*)?wallet\b",
            r"(?i)\btransfer\s*funds?\s*to\s*(?:telegram|direct)\s*(?:admin|wallet|address)\b",
            r"(?i)\bno\s*kyc\s*required\b",
            r"(?i)\broute\s*(?:payments?|capital)\s*through\s*unverified\s*escrow\b",
        ],
        remediation_advice=(
            "Enforce FATF Recommendation 16 identity verification and mandate licensed institutional "
            "custodian escrow for client asset transfers."
        ),
    ),
    # Tier 2 High Suspicion: Extortionate lockups and exit barriers
    RegulatoryRule(
        rule_id="LOCK-001",
        rule_name="Extortionate Mandatory Capital Lockup Interval",
        category="Liquidity Restriction",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=20,
        patterns=[
            r"(?i)\b(?:mandatory\s*)?(?:1[2-9]|[2-9]\d+)[-\s]*months?\s*(?:mandatory\s*)?lock[\s-]?up(?:\s*period)?\b",
            r"(?i)\bmandatory\s*lock[\s-]?up\s*period\s*of\s*(?:1[2-9]|[2-9]\d+)\s*months?\b",
            r"(?i)\block[\s-]?up\s*(?:period\s*)?(?:of\s*|for\s*)?(?:1[2-9]|[2-9]\d+)\s*months?\b",
            r"(?i)\bcapital\s*(?:frozen|locked)\s*(?:for\s*)?(?:1[2-9]|[2-9]\d+)\s*months?\b",
            r"(?i)\block[\s-]?up\s*interval\s*exceeding\s*365\s*days\b",
            r"(?i)\block[\s-]?up\s*period\s*of\s*\d+\s*months\b",
            r"(?i)\bmandatory\s*(?:1[2-9]|[2-9]\d+)[-\s]*months?\s*lock[\s-]?up\b",
        ],
        remediation_advice=(
            "Restrict capital lock-up horizons to commercially reasonable liquidity windows "
            "(typically 90 days or less for retail pooled instruments)."
        ),
    ),
    RegulatoryRule(
        rule_id="LOCK-002",
        rule_name="Punitive Early Redemption Principal Forfeiture",
        category="Exit Barriers",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=20,
        patterns=[
            r"(?i)\bearly\s*(?:withdrawal|exit|redemption)\b.{0,50}?(?:strips?|incurs?|deducts?|penalt(?:y|ies))\s*(?:of\s*)?(?:[3-9]\d|100)%",
            r"(?i)\bearly\s*(?:withdrawal|exit|redemption)\b.{0,50}?(?:[3-9]\d|100)%\s*(?:penalty|fee)?",
            r"(?i)\b(?:strips?|incurs?|deducts?)\s*(?:[3-9]\d|100)%\s*(?:penalty|fee)?",
            r"(?i)\bearly\s*(?:withdrawal|exit|redemption)\s*(?:penalty|fee)\b",
            r"(?i)\bearly\s*withdrawal\s*penalty\s*fees\b",
            r"(?i)\bwithdrawal\s*fee\s*strips\s*(?:[3-9]\d|100)%",
            r"(?i)\bforfeiture\s*of\s*(?:initial\s*)?principal\s*upon\s*early\s*exit\b",
            r"(?i)\bpenalty\s*(?:fees\s*)?strip[s]?\s*\d+%",
            r"(?i)\bpenalty\s*of\s*\d+%",
        ],
        remediation_advice=(
            "Cap early liquidation fees strictly to verified administrative expenses (<= 3%) "
            "and eliminate referral-conditioned redemption restrictions."
        ),
    ),
    # Tier 2 High Suspicion: Contractual asymmetry and unilateral amendments
    RegulatoryRule(
        rule_id="UNFAIR-001",
        rule_name="Unilateral Discretionary Contract Modification Right",
        category="Contractual Asymmetry",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=20,
        patterns=[
            r"(?i)\bwithout\s+prior\s+notice\b",
            r"(?i)\bat\s+(?:its\s+)?sole\s+discretion\b",
            r"(?i)\breserves?\s+the\s+right\s+to\s+(?:modify|alter|amend)\s+terms\b",
            r"(?i)\byield\s*rates?\s*may\s*be\s*altered\b",
            r"(?i)\bunilaterally\s+(?:alter|amend|modify)\b",
        ],
        remediation_advice=(
            "Mandate mutual bilateral consent and a minimum statutory 30-day advance electronic "
            "notice protocol prior to executing material covenant alterations."
        ),
    ),
    RegulatoryRule(
        rule_id="UNFAIR-002",
        rule_name="Absolute Platform Liability & System Exploit Disclaimer",
        category="Liability Disclaimer",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=20,
        patterns=[
            r"(?i)\babsolves?\s+(?:the\s+)?company\s+of\s+all\s+liability\b",
            r"(?i)\bno\s*liability\s*for\s*(?:smart\s*contract\s*failure|exploits?|insolvency)\b",
            r"(?i)\bparticipants?\s*waive\s*all\s*statutory\s*rights\b",
        ],
        remediation_advice=(
            "Stipulate verifiable fiduciary liability boundaries. Blanket consumer liability "
            "waivers for gross negligence remain legally unenforceable across major jurisdictions."
        ),
    ),
    # Tier 2 High Suspicion: Technological jargon masking revenue voids
    RegulatoryRule(
        rule_id="TECH-001",
        rule_name="Algorithmic Buzzword Obfuscation & Insulated Volatility",
        category="Technological Obfuscation",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.FATF_HYIP,
        weight=20,
        patterns=[
            r"(?i)\bautonomous\s*(?:liquidity|arbitrage|neural)\b",
            r"(?i)\balgorithmic\s*arbitrage\b",
            r"(?i)\bquantum\s*(?:vault|arbitrage|ai\s*engine)\b",
            r"(?i)\bcomplete\s*insulation\s*from\s*(?:downside|market|principal)\s*volatility\b",
            r"(?i)\balgorithmic\s*distribution\s*(?:benchmark|without\s*market\s*risk)?\b",
            r"(?i)\bwealth\s*system\b",
            r"(?i)\b100%\s*capital\s*protection\b",
            r"(?i)autonomous\s*(?:liquidity|arbitrage)",
            r"(?i)algorithmic\s*distribution\s*benchmark",
        ],
        remediation_advice=(
            "Publish certified mathematical audit whitepapers detailing execution mechanics "
            "and disclaim directional market impairment exposures prominently."
        ),
    ),
    RegulatoryRule(
        rule_id="PYRAMID-002",
        rule_name="Mandatory License Package or Starter Node Prerequisite",
        category="Recruitment Compensation",
        severity=_HIGH,
        regulatory_framework=RegulatoryFramework.FTC_KOSCOT,
        weight=20,
        patterns=[
            r"(?i)\bmust\s*purchase\s*an?\s*(?:ai\s*|starter\s*|membership\s*)?package\b",
            r"(?i)\bstarter\s*(?:pack|node|tier|license)\s*to\s*qualify\b",
            r"(?i)\bmandatory\s*(?:package|license|activation)\s*purchase\b",
        ],
        remediation_advice="Eliminate mandatory internal package fees required to unlock statutory earnings.",
    ),
    # Tier 3 Cautionary: Offshore secrecy jurisdictions and evasive arbitration
    RegulatoryRule(
        rule_id="JUR-001",
        rule_name="Offshore Secrecy Haven & Forum Evasion",
        category="Jurisdiction Evasion",
        severity=_MEDIUM,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=10,
        patterns=[
            r"(?i)\b(?:laws|jurisdiction|governed\s*by|arbitration)\s*(?:of|in)?\s*(?:Vanuatu|Seychelles|BVI|British\s+Virgin\s+Islands|Marshall\s+Islands|Cayman(?:\s*Islands)?|Saint\s+Vincent)\b",
            r"(?i)\barbitration\s+strictly\s+conducted\s+in\s+offshore\s+tribunals\b",
        ],
        remediation_advice=(
            "Subject contract covenants to recognized sovereign commercial jurisdictions "
            "(e.g., State of Delaware, England & Wales, or Singapore)."
        ),
    ),
    RegulatoryRule(
        rule_id="UNFAIR-004",
        rule_name="Offshore Secrecy Venue & Disproportionate Arbitration Costs",
        category="Jurisdiction Evasion",
        severity=_MEDIUM,
        regulatory_framework=RegulatoryFramework.UNFAIR_TERMS,
        weight=10,
        patterns=[
            r"(?i)\bdisputes?\s*resolved\s*exclusively\s*via\s*arbitration\s*in\s*vanuatu\b",
            r"(?i)\barbitration\s*filing\s*fees\s*borne\s*entirely\s*by\s*claimant\b",
            r"(?i)\barbitration\s+in\s+(?:vanuatu|seychelles|cayman)\b",
        ],
        remediation_advice="Provide accessible domestic dispute resolution forums for retail investors.",
    ),
    # Tier 3 Cautionary: Coercive psychological manipulation and urgency
    RegulatoryRule(
        rule_id="FOMO-001",
        rule_name="Coercive Artificial Scarcity & Psychological Urgency",
        category="Psychological Manipulation",
        severity=_MEDIUM,
        regulatory_framework=RegulatoryFramework.FATF_HYIP,
        weight=10,
        patterns=[
            r"(?i)\bexclusive\s*(?:founder|vip)\s*slots?\s*(?:limited|closing)\b",
            r"(?i)\boffering\s*closes\s*in\s*(?:24|48)\s*hours\b",
            r"(?i)\binstant\s*wealth\s*window\s*closing\b",
            r"(?i)\bguaranteed\s*allocation\s*strictly\s*capped\b",
        ],
        remediation_advice=(
            "Remove coercive high-pressure solicitation timelines. Ensure prospective "
            "participants have adequate statutory deliberation intervals before capital commitment."
        ),
    ),
]

_RULE_MAP: dict[str, RegulatoryRule] = {rule.rule_id: rule for rule in REGULATORY_RULE_CATALOG}


def _validate_all_catalog_patterns() -> None:
    """Verifies syntactic validity of codified regex patterns at import time."""
    for rule in REGULATORY_RULE_CATALOG:
        for pattern in rule.patterns:
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as err:
                raise ValueError(f"Invalid regex pattern in rule {rule.rule_id}: {err}") from err


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
    """Catalog registry managing codified statutory inspection rules."""

    RULES: list[RegulatoryRule] = REGULATORY_RULE_CATALOG
    rules: list[RegulatoryRule] = REGULATORY_RULE_CATALOG

    def __init__(self, custom_rules: list[RegulatoryRule] | None = None) -> None:
        if custom_rules is not None:
            self._rules: list[RegulatoryRule] = list(custom_rules)
            self._instance_map: dict[str, RegulatoryRule] = {
                rule.rule_id: rule for rule in self._rules
            }
        else:
            self._rules = list(REGULATORY_RULE_CATALOG)
            self._instance_map = dict(_RULE_MAP)

    @classmethod
    def get_rules(cls) -> list[RegulatoryRule]:
        return list(cls.RULES)

    @classmethod
    def get_all_rules(cls) -> list[RegulatoryRule]:
        return list(cls.RULES)

    @classmethod
    def get_rule_by_id(cls, rule_id: str) -> RegulatoryRule | None:
        return _RULE_MAP.get(rule_id)

    @classmethod
    def get_rules_by_framework(cls, framework: RegulatoryFramework) -> list[RegulatoryRule]:
        return [rule for rule in cls.RULES if rule.regulatory_framework == framework]

    @classmethod
    def get_rules_by_category(cls, category: str) -> list[RegulatoryRule]:
        target = category.strip().lower()
        return [rule for rule in cls.RULES if rule.category.strip().lower() == target]

    @classmethod
    def get_rules_by_severity(cls, severity: Any) -> list[RegulatoryRule]:
        return [rule for rule in cls.RULES if rule.severity == severity]

    @property
    def all_rules(self) -> list[RegulatoryRule]:
        return list(self._rules)

    def find_by_id(self, rule_id: str) -> RegulatoryRule | None:
        return self._instance_map.get(rule_id)

    def __iter__(self) -> Iterator[RegulatoryRule]:
        return iter(self._rules)

    def __len__(self) -> int:
        return len(self._rules)

    def __getitem__(self, item: Any) -> Any:
        return self._rules[item]

    def __contains__(self, item: Any) -> bool:
        return item in self._rules


RULES = REGULATORY_RULE_CATALOG
rules_catalog = REGULATORY_RULE_CATALOG
get_rules = RegulatoryCatalog.get_rules


def get_catalog() -> RegulatoryCatalog:
    """Factory function returning an initialized RegulatoryCatalog instance."""
    return RegulatoryCatalog()
