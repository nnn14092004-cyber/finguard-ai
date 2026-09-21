"""Mathematical Risk Scoring Engine for FinGuard-AI.

Implements the multi-dimensional weighted scoring formula:
    S = min(100, sum(w_i * c_i))
and decomposes predatory patterns into a 4-dimensional regulatory risk vector
(Yield Risk, Structural Risk, Liquidity Risk, Legal/Jurisdictional Risk)
aligned with the FinGuard Global Knowledge Base.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

from src.domain.enums import RegulatoryFramework, RiskSeverity, RiskTier
from src.domain.models import (
    AuditAssessmentReport,
    ClauseFinding,
    DocumentPayload,
    MultiDimensionalRiskVector,
    ScoringBreakdown,
    SemanticFinding,
)


class ScoringEngine:
    """Calculates weighted suspicion metrics and maps findings to executive risk tiers."""

    @classmethod
    def evaluate(
        cls,
        payload: DocumentPayload,
        *args: Any,
        **kwargs: Any,
    ) -> AuditAssessmentReport:
        """Consolidates findings into an authoritative AuditAssessmentReport.

        Defensively supports multiple invocation signatures across pipeline callers
        and unit test suites:
            evaluate(payload, heuristic_findings, semantic_findings)
            evaluate(payload, findings=..., semantic_findings=...)
            evaluate(payload, heuristic_list)
        """
        # Resolve heuristic findings from args or kwargs
        heuristic_findings: Sequence[ClauseFinding] = []
        if args:
            heuristic_findings = args[0]
        elif "heuristic_findings" in kwargs:
            heuristic_findings = kwargs["heuristic_findings"]
        elif "findings" in kwargs:
            heuristic_findings = kwargs["findings"]

        # Resolve semantic findings from args or kwargs
        semantic_findings: Sequence[SemanticFinding] = []
        if len(args) > 1:
            semantic_findings = args[1]
        elif "semantic_findings" in kwargs:
            semantic_findings = kwargs.get("semantic_findings") or []

        t1_count = 0
        t2_count = 0
        t3_count = 0
        raw_score = 0

        # Heuristic findings aggregation
        for h in heuristic_findings:
            raw_score += h.weight
            if h.severity == RiskSeverity.TIER_1_CRITICAL:
                t1_count += 1
            elif h.severity == RiskSeverity.TIER_2_HIGH:
                t2_count += 1
            elif h.severity == RiskSeverity.TIER_3_CAUTIONARY:
                t3_count += 1

        # Semantic findings aggregation
        for s in semantic_findings:
            if s.implicit_risk_level == RiskSeverity.TIER_1_CRITICAL:
                raw_score += 40
                t1_count += 1
            elif s.implicit_risk_level == RiskSeverity.TIER_2_HIGH:
                raw_score += 20
                t2_count += 1
            elif s.implicit_risk_level == RiskSeverity.TIER_3_CAUTIONARY:
                raw_score += 10
                t3_count += 1

        capped_score = min(100, raw_score)
        risk_tier = cls._determine_risk_tier(capped_score)
        risk_vector = cls._calculate_risk_vector(heuristic_findings, semantic_findings)

        remediation_actions = cls._synthesize_remediation(heuristic_findings, semantic_findings)
        executive_summary = cls._generate_executive_summary(
            payload.file_name, capped_score, risk_tier, t1_count, t2_count, t3_count
        )

        return AuditAssessmentReport(
            document_id=payload.document_id,
            file_name=payload.file_name,
            suspicion_score=capped_score,
            risk_tier=risk_tier,
            risk_vector=risk_vector,
            scoring_breakdown=ScoringBreakdown(
                tier_1_critical_count=t1_count,
                tier_2_high_count=t2_count,
                tier_3_cautionary_count=t3_count,
                raw_score=raw_score,
                capped_score=capped_score,
            ),
            total_findings=len(heuristic_findings) + len(semantic_findings),
            findings=list(heuristic_findings),
            semantic_findings=list(semantic_findings),
            executive_summary=executive_summary,
            remediation_actions=remediation_actions,
        )

    @staticmethod
    def _determine_risk_tier(score: int) -> RiskTier:
        """Maps quantitative score to statutory qualitative risk tier."""
        if score >= 75:
            return RiskTier.RED_FLAG
        if score >= 50:
            return RiskTier.ORANGE
        if score >= 25:
            return RiskTier.YELLOW
        return RiskTier.GREEN

    @staticmethod
    def _calculate_risk_vector(
        heuristic_findings: Sequence[ClauseFinding],
        semantic_findings: Sequence[SemanticFinding],
    ) -> MultiDimensionalRiskVector:
        """Decomposes violations across Yield, Structural, Liquidity, and Legal axes."""
        yield_pts = 0
        struct_pts = 0
        liq_pts = 0
        legal_pts = 0

        for h in heuristic_findings:
            cat = (h.category or "").lower()
            framework = h.regulatory_framework

            if (
                "yield" in cat
                or "obfuscation" in cat
                or framework == RegulatoryFramework.FATF_FCA_HYIP
            ):
                yield_pts += h.weight
            elif (
                "pyramid" in cat
                or "recruit" in cat
                or "securities" in cat
                or "pay to play" in cat
                or framework in [RegulatoryFramework.FTC_IOSCO_PYRAMID, RegulatoryFramework.SEC_HOWEY_DOCTRINE]
            ):
                struct_pts += h.weight
            elif "liquidity" in cat or "lock" in cat:
                liq_pts += h.weight
            elif "jurisdiction" in cat or "manipulation" in cat or framework == RegulatoryFramework.UNFAIR_CONTRACT_TERMS:
                legal_pts += h.weight

        for s in semantic_findings:
            topic = (s.clause_topic or "").lower()
            relevance = s.regulatory_relevance

            if "basis points" in topic or "yield" in topic or relevance == RegulatoryFramework.FATF_FCA_HYIP:
                yield_pts += 40
            elif "downside" in topic or "pyramid" in topic or relevance in [RegulatoryFramework.FTC_IOSCO_PYRAMID, RegulatoryFramework.SEC_HOWEY_DOCTRINE]:
                struct_pts += 40
            elif "liquidity" in topic:
                liq_pts += 20
            else:
                legal_pts += 20

        return MultiDimensionalRiskVector(
            yield_risk=min(100, yield_pts),
            structural_risk=min(100, struct_pts),
            liquidity_risk=min(100, liq_pts),
            legal_risk=min(100, legal_pts),
        )

    @staticmethod
    def _synthesize_remediation(
        heuristic_findings: Sequence[ClauseFinding],
        semantic_findings: Sequence[SemanticFinding],
    ) -> List[str]:
        """Synthesizes deduplicated corrective guidance strings."""
        seen = set()
        actions: List[str] = []

        for h in heuristic_findings:
            if h.remediation_advice and h.remediation_advice not in seen:
                seen.add(h.remediation_advice)
                actions.append(h.remediation_advice)

        for s in semantic_findings:
            if s.deceptive_intent and s.deceptive_intent not in seen:
                seen.add(s.deceptive_intent)
                actions.append(s.deceptive_intent)

        # Statutory baseline recommendation when no predatory clauses are detected
        if not actions:
            actions.append(
                "Document demonstrates standard commercial balance. Ensure periodic legal and counterparty compliance reviews."
            )

        return actions

    @staticmethod
    def _generate_executive_summary(
        file_name: str,
        score: int,
        tier: RiskTier,
        t1: int,
        t2: int,
        t3: int,
    ) -> str:
        """Generates a high-level executive audit summary."""
        return (
            f"Audit completed for '{file_name}'. Suspicion Score: {score}/100 ({tier.value}). "
            f"Violations breakdown: {t1} Critical (Tier 1), {t2} High (Tier 2), {t3} Cautionary (Tier 3). "
            f"Regulatory status: {'UNACCEPTABLE FINANCIAL RISK' if tier == RiskTier.RED_FLAG else 'CONDITIONAL RISK'}."
        )