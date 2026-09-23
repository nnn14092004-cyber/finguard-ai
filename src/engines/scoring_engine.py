"""Mathematical Risk Scoring Engine for FinGuard-AI.

Synthesizes deterministic heuristic violations and contextual semantic audit findings
into a normalized scalar Suspicion Score S in [0, 100], determines the governing RiskTier,
and decomposes exposure into an orthogonal four-dimensional risk vector:
R = (Yield Risk, Structural Risk, Liquidity Risk, Legal Risk).
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from src.core.config import get_settings
from src.domain.enums import RegulatoryFramework, RiskTier
from src.domain.models import AuditAssessmentReport, DocumentPayload, MultiDimensionalRiskVector


class ScoringEngine:
    """Enterprise risk scoring matrix and assessment report synthesizer."""

    def __init__(self) -> None:
        """Initializes regulatory scoring thresholds with centralized settings fallback."""
        try:
            settings = get_settings()
            self._red_flag_threshold: int = settings.RED_FLAG_THRESHOLD
            self._orange_threshold: int = settings.ORANGE_FLAG_THRESHOLD
            self._yellow_threshold: int = settings.YELLOW_FLAG_THRESHOLD
        except Exception:
            self._red_flag_threshold = 75
            self._orange_threshold = 50
            self._yellow_threshold = 25

    @classmethod
    def evaluate(
        cls,
        payload: DocumentPayload,
        heuristic_findings: list[Any] | None = None,
        semantic_findings: list[Any] | None = None,
        findings: list[Any] | None = None,
    ) -> AuditAssessmentReport:
        """Unified class-level entry point supporting legacy callers and modern pipelines."""
        engine = cls()
        return engine.synthesize_assessment(
            payload=payload,
            heuristic_findings=heuristic_findings,
            semantic_findings=semantic_findings,
            findings=findings,
        )

    def compute_suspicion_score(
        self,
        findings: list[Any],
        semantic_findings: list[Any],
    ) -> int:
        """Calculates bounded aggregate suspicion score: S = min(100, max(0, sum(w_i * c_i)))."""
        score: int = 0
        seen_rules: set[str] = set()

        for f in findings:
            rule_id = getattr(f, "rule_id", "")
            weight = getattr(f, "weight", 0)
            if rule_id and rule_id not in seen_rules:
                score += weight
                seen_rules.add(rule_id)

        for sf in semantic_findings:
            penalty = getattr(sf, "penalty_weight", 0) or getattr(sf, "weight", 0)
            score += penalty

        return min(100, max(0, score))

    def determine_risk_tier(self, score: int) -> RiskTier:
        """Maps quantitative score to international regulatory classification tiers."""
        if score >= self._red_flag_threshold:
            return RiskTier.RED_FLAG
        if score >= self._orange_threshold:
            return RiskTier.ORANGE
        if score >= self._yellow_threshold:
            return RiskTier.YELLOW
        return RiskTier.GREEN

    def compute_risk_vector(
        self,
        findings: list[Any],
        semantic_findings: list[Any],
    ) -> MultiDimensionalRiskVector:
        """Decomposes regulatory exposure into an orthogonal 4D risk vector."""
        yield_score: int = 0
        structural_score: int = 0
        liquidity_score: int = 0
        legal_score: int = 0

        rule_ids = {getattr(f, "rule_id", "") for f in findings}
        fatf_frameworks = {
            RegulatoryFramework.FATF_HYIP,
            getattr(RegulatoryFramework, "FATF_FCA_HYIP", RegulatoryFramework.FATF_HYIP),
        }
        howey_frameworks = {
            RegulatoryFramework.HOWEY_TEST,
            getattr(RegulatoryFramework, "SEC_HOWEY", RegulatoryFramework.HOWEY_TEST),
        }
        koscot_frameworks = {
            RegulatoryFramework.FTC_KOSCOT,
            getattr(RegulatoryFramework, "KOSCOT", RegulatoryFramework.FTC_KOSCOT),
        }

        # 1. Yield Risk (HYIP promises, velocity benchmarks, capital guarantees)
        if "HYIP-001" in rule_ids:
            yield_score += 70
        if "TECH-001" in rule_ids:
            yield_score += 30
        for f in findings:
            framework = getattr(f, "regulatory_framework", None)
            rule_id = getattr(f, "rule_id", "")
            weight = getattr(f, "weight", 0)
            category = str(getattr(f, "category", "")).upper()
            if framework in fatf_frameworks and rule_id not in {"HYIP-001", "TECH-001"}:
                yield_score += weight
            elif "YIELD" in category and rule_id not in {"HYIP-001", "TECH-001"}:
                yield_score += weight

        # 2. Structural Risk (Howey passive pooling, FTC Koscot pyramid recruitments)
        if "HOWEY-001" in rule_ids:
            structural_score += 40
        if "MLM-001" in rule_ids or "PYRAMID-001" in rule_ids or "PYR-001" in rule_ids:
            structural_score += 40
        if "PYRAMID-002" in rule_ids:
            structural_score += 20
        for f in findings:
            framework = getattr(f, "regulatory_framework", None)
            rule_id = getattr(f, "rule_id", "")
            weight = getattr(f, "weight", 0)
            if framework in (howey_frameworks | koscot_frameworks):
                if rule_id not in {
                    "HOWEY-001",
                    "MLM-001",
                    "PYRAMID-001",
                    "PYR-001",
                    "PYRAMID-002",
                }:
                    structural_score += weight

        # 3. Liquidity Risk (Lockup intervals, exit forfeiture, conditional liquidity)
        if "LOCK-001" in rule_ids:
            liquidity_score += 30
        if "LOCK-002" in rule_ids:
            liquidity_score += 30
        for f in findings:
            category = str(getattr(f, "category", "")).upper()
            rule_id = getattr(f, "rule_id", "")
            weight = getattr(f, "weight", 0)
            if "LIQUIDITY" in category and rule_id not in {"LOCK-001", "LOCK-002"}:
                liquidity_score += weight

        # 4. Legal Risk (Secrecy havens, unilateral modification, AML evasion, liability waivers)
        if "JUR-001" in rule_ids or "UNFAIR-004" in rule_ids:
            legal_score += 20
        if "UNFAIR-001" in rule_ids or "UNFAIR-002" in rule_ids or "AML-001" in rule_ids:
            legal_score += 20
        for f in findings:
            category = str(getattr(f, "category", "")).upper()
            rule_id = getattr(f, "rule_id", "")
            weight = getattr(f, "weight", 0)
            if (
                "JURISDICTION" in category
                or "ABUSIVE" in category
                or "LEGAL" in category
                or "AML" in category
            ) and rule_id not in {"JUR-001", "UNFAIR-004", "UNFAIR-001", "UNFAIR-002", "AML-001"}:
                legal_score += weight

        # Contextual semantic findings
        for sf in semantic_findings:
            category = str(getattr(sf, "category", "") or getattr(sf, "clause_topic", "")).upper()
            penalty = getattr(sf, "penalty_weight", 0) or getattr(sf, "weight", 0) or 20
            if "YIELD" in category:
                yield_score += penalty
            elif "STRUCTURE" in category or "HOWEY" in category or "PYRAMID" in category:
                structural_score += penalty
            elif "LIQUIDITY" in category or "LOCK" in category:
                liquidity_score += penalty
            elif "LEGAL" in category or "JURISDICTION" in category or "AML" in category:
                legal_score += penalty

        return MultiDimensionalRiskVector(
            yield_risk=min(100, yield_score),
            structural_risk=min(100, structural_score),
            liquidity_risk=min(100, liquidity_score),
            legal_risk=min(100, legal_score),
        )

    def synthesize_assessment(
        self,
        payload: DocumentPayload,
        heuristic_findings: list[Any] | None = None,
        semantic_findings: list[Any] | None = None,
        findings: list[Any] | None = None,
    ) -> AuditAssessmentReport:
        """Synthesizes granular infractions into a unified report adhering to pipeline contract."""
        resolved_findings: list[Any] = []
        if heuristic_findings is not None:
            resolved_findings.extend(heuristic_findings)
        if findings is not None:
            resolved_findings.extend(findings)

        resolved_semantics = semantic_findings or []
        file_name = getattr(payload, "file_name", "document.txt")

        # Cryptographic Provenance (SHA-256 Document Fingerprint)
        raw_text = getattr(payload, "raw_text", "") or getattr(payload, "raw_content", "")
        doc_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

        return self.synthesize_report(
            file_name=file_name,
            findings=resolved_findings,
            semantic_findings=resolved_semantics,
            doc_fingerprint=doc_hash,
        )

    def synthesize_report(
        self,
        file_name: str,
        findings: list[Any],
        semantic_findings: list[Any],
        doc_fingerprint: str | None = None,
    ) -> AuditAssessmentReport:
        """Synthesizes complete regulatory compliance report with remediation guidance."""
        suspicion_score = self.compute_suspicion_score(findings, semantic_findings)
        risk_tier = self.determine_risk_tier(suspicion_score)
        risk_vector = self.compute_risk_vector(findings, semantic_findings)

        total_findings = len(findings) + len(semantic_findings)

        if risk_tier in (RiskTier.RED, RiskTier.RED_FLAG):
            summary = (
                f"CRITICAL REGULATORY HAZARD DETECTED in '{file_name}'. Suspicion Score: {suspicion_score}/100. "
                "Document exhibits severe compounding indicators of an unregistered investment syndicate, "
                "untenable high-yield solicitation, and multi-tier recruitment architecture."
            )
        elif risk_tier == RiskTier.ORANGE:
            summary = (
                f"HIGH REGULATORY SUSPICION in '{file_name}'. Suspicion Score: {suspicion_score}/100. "
                "Document contains predatory contractual clauses, excessive capital lock-ups, or offshore legal evasion."
            )
        elif risk_tier == RiskTier.YELLOW:
            summary = (
                f"CAUTIONARY COMPLIANCE REVIEW REQUIRED for '{file_name}'. Suspicion Score: {suspicion_score}/100. "
                "Non-standard clauses identified requiring legal scrutiny prior to execution."
            )
        else:
            summary = (
                f"STANDARD COMMERCIAL CONTRACT PROFILE for '{file_name}'. Suspicion Score: {suspicion_score}/100. "
                "Zero critical Ponzi, pyramid, or predatory regulatory infractions identified."
            )

        if doc_fingerprint:
            summary += f" [SHA-256 Provenance: {doc_fingerprint[:16]}...]"

        remediation_set: set[str] = set()
        for f in findings:
            advice = getattr(f, "remediation_advice", None) or getattr(
                f, "remediation_guidance", None
            )
            if advice:
                remediation_set.add(advice)
        for sf in semantic_findings:
            advice = getattr(sf, "remediation_guidance", None) or getattr(
                sf, "remediation_advice", None
            )
            if advice:
                remediation_set.add(advice)

        if not remediation_set:
            remediation_set.add(
                "No immediate statutory remediation required. Contract adheres to commercial baselines."
            )

        return AuditAssessmentReport(
            document_id=str(uuid.uuid4()),
            file_name=file_name,
            suspicion_score=suspicion_score,
            risk_tier=risk_tier,
            risk_vector=risk_vector,
            total_findings=total_findings,
            findings=findings,
            semantic_findings=semantic_findings,
            executive_summary=summary,
            remediation_actions=sorted(remediation_set),
        )
