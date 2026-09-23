"""Statutory enumeration types for FinGuard-AI compliance auditing."""

from __future__ import annotations

from enum import Enum


class RiskTier(str, Enum):
    """Aggregate risk classification tiers based on computed suspicion score."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"

    # Backward compatibility aliases
    RED_FLAG = "RED"
    CRITICAL = "RED"


class Severity(str, Enum):
    """Penalty weighting tiers mapped directly to statutory infraction severity."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    # Backward compatibility aliases for statutory penalty tiers
    TIER_1_CRITICAL = "CRITICAL"
    TIER_2_HIGH = "HIGH"
    TIER_3_CAUTIONARY = "MEDIUM"
    TIER_3_CAUTION = "MEDIUM"
    TIER_3_MEDIUM = "MEDIUM"
    TIER_4_LOW = "LOW"
    CAUTIONARY = "MEDIUM"
    CAUTION = "MEDIUM"


RiskSeverity = Severity
RuleSeverity = Severity


class RegulatoryFramework(str, Enum):
    """Governing international financial regulatory bodies and statutory doctrines."""

    HOWEY_TEST = "HOWEY_TEST"
    SEC_HOWEY = "HOWEY_TEST"
    HOWEY = "HOWEY_TEST"

    FTC_KOSCOT = "FTC_KOSCOT"
    FTC_PYRAMID = "FTC_KOSCOT"
    KOSCOT = "FTC_KOSCOT"
    PYRAMID = "FTC_KOSCOT"

    FATF_HYIP = "FATF_HYIP"
    FATF_FCA_HYIP = "FATF_HYIP"
    FATF = "FATF_HYIP"

    UNFAIR_TERMS = "UNFAIR_TERMS"
    UNFAIR = "UNFAIR_TERMS"
    UNFAIR_TERMS_ACT = "UNFAIR_TERMS"

    JURISDICTION_EVASION = "JURISDICTION_EVASION"
    JURISDICTION_LAUNDERING = "JURISDICTION_EVASION"
    JURISDICTION = "JURISDICTION_EVASION"
