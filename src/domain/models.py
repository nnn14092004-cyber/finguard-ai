"""Domain Models and Data Contracts for FinGuard-AI.

Defines Pydantic V2 schemas for audit requests, violation findings,
multi-dimensional risk vectors, scoring breakdowns, and comprehensive assessment reports.
"""

from __future__ import annotations

import uuid
from typing import Any, List, Optional
from pydantic import BaseModel, Field, model_validator

from src.domain.enums import RegulatoryFramework, RiskSeverity, RiskTier


class ClauseFinding(BaseModel):
    """Deterministic violation identified via heuristic regex scanning."""

    rule_id: str
    rule_name: str
    severity: RiskSeverity
    weight: int
    category: str
    matched_text: str
    start_index: int
    end_index: int
    regulatory_framework: RegulatoryFramework
    remediation_advice: str


class SemanticFinding(BaseModel):
    """Contextual violation identified via deep NLP semantic analysis."""

    clause_topic: str
    deceptive_intent: str
    extracted_text: str
    implicit_risk_level: RiskSeverity
    regulatory_relevance: RegulatoryFramework
    confidence_score: float = Field(ge=0.0, le=1.0)


class MultiDimensionalRiskVector(BaseModel):
    """Multi-dimensional risk breakdown across key predatory domains."""

    yield_risk: int = Field(default=0, ge=0, le=100)
    structural_risk: int = Field(default=0, ge=0, le=100)
    liquidity_risk: int = Field(default=0, ge=0, le=100)
    legal_risk: int = Field(default=0, ge=0, le=100)


# Defensive alias for flexible naming conventions
RiskVector = MultiDimensionalRiskVector


class ScoringBreakdown(BaseModel):
    """Detailed audit metrics accounting for severity distribution and score caps."""

    tier_1_critical_count: int = Field(default=0, ge=0)
    tier_2_high_count: int = Field(default=0, ge=0)
    tier_3_cautionary_count: int = Field(default=0, ge=0)
    raw_score: int = Field(default=0, ge=0)
    capped_score: int = Field(default=0, ge=0, le=100)


class AuditAssessmentReport(BaseModel):
    """Official FinGuard-AI compliance audit report."""

    document_id: str
    file_name: str
    suspicion_score: int = Field(ge=0, le=100)
    risk_tier: RiskTier
    risk_vector: MultiDimensionalRiskVector
    scoring_breakdown: ScoringBreakdown
    total_findings: int
    findings: List[ClauseFinding] = Field(default_factory=list)
    semantic_findings: List[SemanticFinding] = Field(default_factory=list)
    executive_summary: str
    remediation_actions: List[str] = Field(default_factory=list)


# Defensive aliases
AuditReport = AuditAssessmentReport
RuleFinding = ClauseFinding


class ContractAuditRequest(BaseModel):
    """Inbound REST API request payload for raw contract text auditing."""

    document_title: str = Field(default="contract_draft.txt")
    content: str = Field(min_length=1)


class DocumentPayload(BaseModel):
    """Internal document payload wrapper across ingestion, scanning, and pipeline."""

    document_id: str = Field(default="")
    file_name: str = "document.txt"
    raw_content: str = ""
    normalized_content: str = ""
    character_count: int = 0
    content: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def harmonize_payload_contracts(cls, data: Any) -> Any:
        """Defensively bridges content and raw_content attributes across callers."""
        if isinstance(data, dict):
            raw = data.get("raw_content") or data.get("content") or ""
            norm = data.get("normalized_content") or raw
            data.setdefault("raw_content", raw)
            data.setdefault("content", raw)
            data.setdefault("normalized_content", norm)
            data.setdefault("character_count", len(norm))
            if not data.get("document_id"):
                data["document_id"] = str(uuid.uuid4())
            data.setdefault("file_name", "document.txt")
        return data


class RuleDefinition(BaseModel):
    """Internal schema representing a codified regulatory heuristic rule."""

    model_config = {"arbitrary_types_allowed": True}

    rule_id: str
    rule_name: str
    severity: RiskSeverity
    weight: int
    category: str
    pattern: Any
    regulatory_framework: RegulatoryFramework
    remediation_advice: str