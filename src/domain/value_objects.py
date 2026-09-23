"""Domain Enumerations for FinGuard-AI Regulatory Compliance Pipeline.

Defines discrete regulatory jurisdictions, risk tiers, statutory frameworks,
and violation severity penalty classifications.
"""

from __future__ import annotations

from enum import Enum


class RiskTier(str, Enum):
    """Aggregate risk classification tiers based on computed suspicion score."""

    GREEN = "GREEN"  # 0 - 24 points: Standard commercial contract
    YELLOW = "YELLOW"  # 25 - 49 points: Cautionary / Unbalanced clauses
    ORANGE = "ORANGE"  # 50 - 74 points: High suspicion / Predatory patterns
    RED_FLAG = "RED_FLAG"  # 75 - 100 points: Critical Ponzi / Scam / Illegal scheme


class RegulatoryFramework(str, Enum):
    """Governing international financial regulatory bodies and doctrines."""

    SEC_HOWEY = "SEC_HOWEY"  # U.S. Securities & Exchange Commission (Howey Doctrine)
    FTC_KOSCOT = "FTC_KOSCOT"  # Federal Trade Commission (Pyramid Scheme Test)
    FATF_HYIP = "FATF_HYIP"  # Financial Action Task Force (High-Yield Fraud)
    FCA_UK = "FCA_UK"  # UK Financial Conduct Authority (Consumer Protection)
    UNFAIR_TERMS = "UNFAIR_TERMS"  # Cross-Border Unfair Contract Terms Directive


class Severity(str, Enum):
    """Penalty weighting tiers mapped directly to statutory infraction severity."""

    CRITICAL = "CRITICAL"  # +40 points: Guaranteed yields, binary MLM, unregistered securities
    HIGH = "HIGH"  # +20 points: Unilateral modification, predatory lock-up >12 months
    MEDIUM = "MEDIUM"  # +10 points: Offshore secrecy haven jurisdiction, FOMO urgency
    LOW = "LOW"  # Informational compliance notice
    CAUTIONARY = "CAUTIONARY"  # Regulatory review notice


# Backward compatibility alias for legacy heuristic engines
RuleSeverity = Severity
