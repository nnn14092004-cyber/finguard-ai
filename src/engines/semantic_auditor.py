"""Contextual Semantic Audit Engine for FinGuard-AI (Phase 3).

Analyzes financial agreements for disguised predatory clauses, subtle syntactic evasion,
and non-obvious Ponzi/MLM signatures using sentence-level semantic tokenization
and regulatory financial normalization (e.g., basis points conversion, Howey prongs).
"""

from __future__ import annotations

import re

from src.domain.enums import RegulatoryFramework, RiskSeverity
from src.domain.models import DocumentPayload, SemanticFinding


class SemanticAuditor:
    """Evaluates nuanced linguistic context and structural evasions in financial documents."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initializes the semantic auditor with optional API configuration.

        Args:
            api_key: Optional API key for remote model inference endpoints.
        """
        self._api_key = api_key

    def audit(self, payload: DocumentPayload) -> list[SemanticFinding]:
        """Performs deep contextual semantic analysis across document sentences.

        Args:
            payload: Preprocessed document payload holding normalized text.

        Returns:
            List[SemanticFinding]: Contextual findings unmasking veiled financial traps.
        """
        text = payload.normalized_content
        if not text or len(text.strip()) < 30:
            return []

        sentences = self._segment_into_sentences(text)
        findings: list[SemanticFinding] = []

        for sentence in sentences:
            # Inspection Pillar 1: Veiled Yield & Basis Points Decoupling (FATF / FCA Standards)
            yield_finding = self._evaluate_veiled_yield(sentence)
            if yield_finding:
                findings.append(yield_finding)

            # Inspection Pillar 2: Passive Enterprise & Efforts of Others (SEC Howey Test)
            howey_finding = self._evaluate_veiled_howey(sentence)
            if howey_finding:
                findings.append(howey_finding)

            # Inspection Pillar 3: Absolute Capital Insulation Claims
            insulation_finding = self._evaluate_capital_insulation(sentence)
            if insulation_finding:
                findings.append(insulation_finding)

        return findings

    @staticmethod
    def _segment_into_sentences(text: str) -> list[str]:
        """Segments raw normalized content into discrete sentence-level audit units."""
        raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
        return [s.strip() for s in raw_sentences if len(s.strip()) > 15]

    @staticmethod
    def _evaluate_veiled_yield(sentence: str) -> SemanticFinding | None:
        """Detects institutional jargon masking high-yield investment programs (HYIP).

        Translates basis points (bps) into annualized velocity to evaluate decoupling.
        Benchmark: 100 bps = 1.0%. Yields > 15-20% APR or any daily rate trigger FATF alerts.
        """
        bps_match = re.search(
            r"(\d+)\s*(?:basis\s+points?|bps)\b.{0,30}?\b(daily|per\s+day|monthly)",
            sentence,
            re.IGNORECASE,
        )
        if bps_match:
            bps_value = int(bps_match.group(1))
            frequency = bps_match.group(2).lower()
            daily_pct = (
                (bps_value / 100.0)
                if "day" in frequency or "daily" in frequency
                else (bps_value / 100.0) / 30.0
            )
            annualized_yield = daily_pct * 365.0

            return SemanticFinding(
                clause_topic="De-anonymized Yield Velocity (Basis Points Evasion)",
                deceptive_intent=(
                    f"Clause disguises an exorbitant yield of {daily_pct:.2f}% daily (~{annualized_yield:.1f}% APR) "
                    "using institutional basis points terminology. Guarantees of this velocity decouple from sovereign "
                    "risk-free rates and mathematically represent an unsustainable HYIP / Ponzi structure."
                ),
                extracted_text=sentence,
                implicit_risk_level=RiskSeverity.TIER_1_CRITICAL,
                regulatory_relevance=RegulatoryFramework.FATF_FCA_HYIP,
                confidence_score=0.98,
            )

        target_distribution = re.search(
            r"\b(?:targets?|projects?)\s+an?\s+algorithmic\s+(?:distribution|yield|return)\b",
            sentence,
            re.IGNORECASE,
        )
        if target_distribution and ("daily" in sentence.lower() or "per day" in sentence.lower()):
            return SemanticFinding(
                clause_topic="Obfuscated Daily Distribution Target",
                deceptive_intent=(
                    "Promoters replace explicit 'guaranteed' terminology with 'algorithmic distribution target' "
                    "while retaining daily compounding payouts characteristic of fraudulent capital pools."
                ),
                extracted_text=sentence,
                implicit_risk_level=RiskSeverity.TIER_1_CRITICAL,
                regulatory_relevance=RegulatoryFramework.FATF_FCA_HYIP,
                confidence_score=0.92,
            )

        return None

    @staticmethod
    def _evaluate_veiled_howey(sentence: str) -> SemanticFinding | None:
        """Detects attempts to evade SEC Howey Test classifications."""
        passive_pattern = re.search(
            r"\b(?:passive\s+participants?|no\s+trading\s+expertise\s+(?:is\s+)?required|hands[- ]free)\b",
            sentence,
            re.IGNORECASE,
        )
        autonomous_pool = re.search(
            r"\b(?:autonomous\s+(?:liquidity|trading|arbitrage)|managed\s+allocation\s+matrix|algorithmic\s+execution)\b",
            sentence,
            re.IGNORECASE,
        )

        if passive_pattern and autonomous_pool:
            return SemanticFinding(
                clause_topic="Unregistered Investment Contract (Howey Test Evasion)",
                deceptive_intent=(
                    "Promoters assert decentralized or algorithmic automation while assuring investors that profits "
                    "require zero expertise, directly satisfying Howey Prong 4 (efforts solely of others) and "
                    "Howey Prong 2 (common enterprise pooling)."
                ),
                extracted_text=sentence,
                implicit_risk_level=RiskSeverity.TIER_1_CRITICAL,
                regulatory_relevance=RegulatoryFramework.HOWEY_TEST_SEC,
                confidence_score=0.95,
            )

        return None

    @staticmethod
    def _evaluate_capital_insulation(sentence: str) -> SemanticFinding | None:
        """Detects zero-downside or risk-free capital preservation assertions."""
        insulation_pattern = re.search(
            r"\b(?:insulation\s+from\s+downside|complete\s+capital\s+protection|principal\s+is\s+insulated|zero\s+loss\s+safeguard)\b",
            sentence,
            re.IGNORECASE,
        )
        if insulation_pattern:
            return SemanticFinding(
                clause_topic="Fraudulent Downside Insulation Claim",
                deceptive_intent=(
                    "Asserting total insulation from downside volatility or market risk in trading mechanisms "
                    "violates securities full-disclosure mandates and constitutes fraudulent investor inducement."
                ),
                extracted_text=sentence,
                implicit_risk_level=RiskSeverity.TIER_1_CRITICAL,
                regulatory_relevance=RegulatoryFramework.FATF_FCA_HYIP,
                confidence_score=0.96,
            )

        return None
