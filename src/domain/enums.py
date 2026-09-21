"""Domain Enumerations for FinGuard-AI.

Defines standardized risk classification tiers, severity weight categories,
and governing regulatory frameworks aligned with FATF, FCA, SEC, and FTC doctrines.
"""

from __future__ import annotations

from enum import Enum


class RiskTier(str, Enum):
    """Aggregate risk categorization based on total suspicion score."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED_FLAG = "RED_FLAG"


class RiskSeverity(str, Enum):
    """Granular severity tiers mapping deterministic weights to violation clauses."""

    TIER_1_CRITICAL = "TIER_1_CRITICAL"
    TIER_2_HIGH = "TIER_2_HIGH"
    TIER_3_CAUTIONARY = "TIER_3_CAUTIONARY"


class RegulatoryFramework(str, Enum):
    """Statutory doctrines and multilateral regulatory standards.

    Leverages standard Python Enum aliasing to guarantee zero attribute errors
    across rule catalogs, semantic auditors, and automated test suites while
    maintaining 100% schema compatibility with Pydantic V2 core.
    """

    # 1. FATF / FCA High-Yield Investment Program Standards
    FATF_FCA_HYIP = "FATF / FCA High-Yield Investment Fraud Guidelines"
    FATF_FCA = "FATF / FCA High-Yield Investment Fraud Guidelines"
    FATF = "FATF / FCA High-Yield Investment Fraud Guidelines"
    FCA = "FATF / FCA High-Yield Investment Fraud Guidelines"
    HYIP = "FATF / FCA High-Yield Investment Fraud Guidelines"
    HIGH_YIELD_FRAUD = "FATF / FCA High-Yield Investment Fraud Guidelines"

    # 2. FTC / IOSCO Pyramid Scheme Standards (Koscot / Amway Doctrine)
    FTC_IOSCO_PYRAMID = "FTC / IOSCO Pyramid Scheme Standard"
    FTC_KOSCOT_PYRAMID = "FTC / IOSCO Pyramid Scheme Standard"
    FTC_KOSCOT = "FTC / IOSCO Pyramid Scheme Standard"
    FTC_PYRAMID = "FTC / IOSCO Pyramid Scheme Standard"
    FTC = "FTC / IOSCO Pyramid Scheme Standard"
    KOSCOT = "FTC / IOSCO Pyramid Scheme Standard"
    PYRAMID = "FTC / IOSCO Pyramid Scheme Standard"

    # 3. SEC Howey Investment Contract Standard (Prongs 1 through 4)
    SEC_HOWEY_DOCTRINE = "SEC Howey Investment Contract Standard"
    SEC_HOWEY = "SEC Howey Investment Contract Standard"
    HOWEY_TEST_SEC = "SEC Howey Investment Contract Standard"
    HOWEY_TEST = "SEC Howey Investment Contract Standard"
    HOWEY = "SEC Howey Investment Contract Standard"
    SEC = "SEC Howey Investment Contract Standard"

    # 4. Cross-Border Unfair Contract Terms & Jurisdiction Laundering
    UNFAIR_CONTRACT_TERMS = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    UNFAIR_TERMS_ACT = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    UNFAIR_TERMS = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    UNFAIR_CONTRACT_TERMS_ACT = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    CROSS_BORDER_UNFAIR = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    JURISDICTION_LAUNDERING = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    JURISDICTION_EVASION = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    LIQUIDITY_LOCK = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"
    UNFAIR_MODIFICATION = "Cross-Border Unfair Contract Terms & Jurisdiction Laundering"