"""Domain models and data schemas for FinGuard-AI compliance audit pipeline."""

from __future__ import annotations

import uuid
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.domain.enums import RegulatoryFramework, RiskTier, Severity


class DocumentPayload(BaseModel):
    """Container for contract document ingestion and normalized state."""

    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str = Field(default="unnamed_document.txt")
    raw_text: str = Field(default="")
    raw_content: str = Field(default="")
    normalized_text: str = Field(default="")
    normalized_content: str = Field(default="")
    character_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="after")
    def synchronize_content_fields(self) -> Self:
        """Synchronizes text content fields across primary names and aliases."""
        if self.raw_text and not self.raw_content:
            self.raw_content = self.raw_text
        elif self.raw_content and not self.raw_text:
            self.raw_text = self.raw_content

        if self.normalized_text and not self.normalized_content:
            self.normalized_content = self.normalized_text
        elif self.normalized_content and not self.normalized_text:
            self.normalized_text = self.normalized_content

        if self.character_count == 0:
            self.character_count = len(self.normalized_text or self.raw_text)
        return self


class RegulatoryRule(BaseModel):
    """Codified compliance rule representing international statutory requirements."""

    rule_id: str = Field(..., min_length=2)
    rule_name: str = Field(..., min_length=3)
    category: str = Field(..., min_length=2)
    severity: Severity | str = Field(...)
    regulatory_framework: RegulatoryFramework | str = Field(...)
    weight: int = Field(..., ge=0, le=40)
    pattern: str = Field(default="")
    patterns: list[str] = Field(default_factory=list)
    remediation_advice: str = Field(..., min_length=5)

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="after")
    def reconcile_patterns(self) -> Self:
        """Maintains bidirectional synchronization between single pattern and list."""
        if self.patterns and not self.pattern:
            self.pattern = self.patterns[0]
        elif self.pattern and not self.patterns:
            self.patterns = [self.pattern]
        return self


class Finding(BaseModel):
    """Discrete heuristic violation discovered within an audited document."""

    rule_id: str = Field(...)
    rule_name: str = Field(default="")
    severity: Severity | str = Field(default=Severity.MEDIUM)
    regulatory_framework: RegulatoryFramework | str = Field(
        default=RegulatoryFramework.UNFAIR_TERMS
    )
    weight: int = Field(default=10, ge=0, le=40)
    matched_text: str = Field(default="")
    category: str = Field(default="")
    remediation_advice: str = Field(default="")
    start_index: int = Field(default=0)
    end_index: int = Field(default=0)
    span: Any | None = Field(default=None)

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @property
    def matched_clause(self) -> str:
        return self.matched_text

    @property
    def remediation_guidance(self) -> str:
        return self.remediation_advice


class SemanticFinding(BaseModel):
    """Contextual semantic violation detected by NLP or semantic audit engines."""

    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = Field(default="SEM-001")
    clause_topic: str = Field(default="")
    category: str = Field(default="Regulatory Risk")
    extracted_text: str = Field(default="")
    context_snippet: str = Field(default="")
    matched_text: str = Field(default="")
    deceptive_intent: str = Field(default="")
    implicit_risk_level: str = Field(default="HIGH")
    regulatory_relevance: str = Field(default="")
    severity: Severity | str = Field(default=Severity.HIGH)
    penalty_weight: int = Field(default=20, ge=0, le=40)
    weight: int = Field(default=20, ge=0, le=40)
    remediation_guidance: str = Field(default="")
    remediation_advice: str = Field(default="")
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0)

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="after")
    def reconcile_semantic_fields(self) -> Self:
        """Cross-populates synonymous fields for downstream evaluation layers."""
        text = self.extracted_text or self.context_snippet or self.matched_text
        if not self.extracted_text:
            self.extracted_text = text
        if not self.context_snippet:
            self.context_snippet = text
        if not self.matched_text:
            self.matched_text = text

        remediation = (
            self.remediation_guidance or self.remediation_advice or self.deceptive_intent
        )
        if not self.remediation_guidance:
            self.remediation_guidance = remediation
        if not self.remediation_advice:
            self.remediation_advice = remediation

        if self.clause_topic and self.category in ("", "Regulatory Risk"):
            self.category = self.clause_topic
        elif self.category and not self.clause_topic:
            self.clause_topic = self.category

        if self.penalty_weight != 20 and self.weight == 20:
            self.weight = self.penalty_weight
        elif self.weight != 20 and self.penalty_weight == 20:
            self.penalty_weight = self.weight

        return self


class MultiDimensionalRiskVector(BaseModel):
    """Orthogonal 4D risk vector decomposing regulatory exposure across distinct axes."""

    yield_risk: int = Field(..., ge=0, le=100)
    structural_risk: int = Field(..., ge=0, le=100)
    liquidity_risk: int = Field(..., ge=0, le=100)
    legal_risk: int = Field(..., ge=0, le=100)


class AuditAssessmentReport(BaseModel):
    """Comprehensive compliance assessment report synthesized by the evaluation engine."""

    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str = Field(...)
    suspicion_score: int = Field(..., ge=0, le=100)
    risk_tier: RiskTier = Field(...)
    risk_vector: MultiDimensionalRiskVector = Field(...)
    total_findings: int = Field(default=0, ge=0)
    findings: list[Finding] = Field(default_factory=list)
    semantic_findings: list[Any] = Field(default_factory=list)
    executive_summary: str = Field(...)
    remediation_actions: list[str] = Field(default_factory=list)
    raw_content: str = Field(default="")

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class ContractAuditRequest(BaseModel):
    """Inbound REST request schema for text compliance auditing."""

    content: str = Field(..., min_length=1)
    document_title: str | None = Field(default="contract_draft.txt")


ClauseFinding = Finding
RuleDefinition = RegulatoryRule
ComplianceFinding = Finding
