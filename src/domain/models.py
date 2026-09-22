"""Domain Models and Data Transfer Objects for FinGuard-AI.

Defines defensive Pydantic V2 schemas for document ingestion payloads,
codified statutory rules, granular heuristic and semantic audit findings,
4D risk vectors, and executive compliance assessment reports.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.domain.enums import RegulatoryFramework, RiskSeverity, RiskTier, RuleSeverity, Severity


class DocumentPayload(BaseModel):
    """Immutable contract payload container with dual-field compatibility."""

    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Document unique identifier.")
    file_name: str = Field(default="unnamed_document.txt", description="Originating filename or label.")
    raw_text: str = Field(default="", description="Raw unnormalized textual contract input.")
    normalized_text: str = Field(default="", description="Deobfuscated and Unicode NFKC normalized text.")
    character_count: int = Field(default=0, ge=0, description="Normalized character length.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary ingestion metadata.")

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="before")
    @classmethod
    def reconcile_field_aliases(cls, data: Any) -> Any:
        """Harmonizes raw_content/raw_text and normalized_content/normalized_text transparently."""
        if isinstance(data, dict):
            if "raw_content" in data and not data.get("raw_text"):
                data["raw_text"] = data["raw_content"]
            elif "raw_text" in data and not data.get("raw_content"):
                data["raw_content"] = data["raw_text"]

            if "normalized_content" in data and not data.get("normalized_text"):
                data["normalized_text"] = data["normalized_content"]
            elif "normalized_text" in data and not data.get("normalized_content"):
                data["normalized_content"] = data["normalized_text"]

            if "character_count" not in data:
                data["character_count"] = len(data.get("normalized_text", ""))
        return data

    @property
    def raw_content(self) -> str:
        """Alias for raw_text for backward compatibility."""
        return self.raw_text

    @property
    def normalized_content(self) -> str:
        """Alias for normalized_text for backward compatibility."""
        return self.normalized_text


class RegulatoryRule(BaseModel):
    """Codified compliance rule representing international statutory requirements."""

    rule_id: str = Field(..., min_length=2, description="Canonical rule code (e.g., HOWEY-001).")
    rule_name: str = Field(..., min_length=3, description="Descriptive regulatory violation title.")
    category: str = Field(..., min_length=2, description="Infraction category.")
    severity: Severity = Field(..., description="Penalty severity classification.")
    regulatory_framework: RegulatoryFramework = Field(..., description="Governing regulatory authority.")
    weight: int = Field(..., ge=0, le=40, description="Mathematical score weight contribution.")
    pattern: str = Field(..., min_length=3, description="Compiled regular expression pattern.")
    remediation_advice: str = Field(..., min_length=5, description="Actionable statutory remediation counsel.")

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class Finding(BaseModel):
    """Discrete heuristic violation discovered within an audited document."""

    rule_id: str = Field(..., description="Canonical rule code of the triggered rule.")
    rule_name: str = Field(default="", description="Descriptive violation title.")
    severity: Severity = Field(default=Severity.MEDIUM, description="Severity classification tier.")
    regulatory_framework: RegulatoryFramework = Field(default=RegulatoryFramework.UNFAIR_TERMS, description="Governing statutory doctrine.")
    weight: int = Field(default=10, ge=0, le=40, description="Score penalty weight.")
    matched_text: str = Field(default="", description="Verbatim infringing text extracted from document.")
    category: str = Field(default="", description="Substantive risk classification category.")
    remediation_advice: str = Field(default="", description="Statutory remediation guidance.")
    start_index: int = Field(default=0, description="Zero-indexed start character offset.")
    end_index: int = Field(default=0, description="Zero-indexed end character offset.")
    span: Optional[Any] = Field(default=None, description="Exact document coordinates.")

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @property
    def matched_clause(self) -> str:
        """Alias for matched_text to maintain domain value object parity."""
        return self.matched_text

    @property
    def remediation_guidance(self) -> str:
        """Alias for remediation_advice to maintain domain value object parity."""
        return self.remediation_advice


class SemanticFinding(BaseModel):
    """Contextual semantic finding produced by the NLP evasion auditor."""

    rule_id: str = Field(default="SEM-001", description="Canonical semantic violation code.")
    category: str = Field(default="Regulatory Risk", description="Regulatory risk domain classification.")
    context_snippet: str = Field(default="", description="Contextual excerpt illustrating predatory intent.")
    penalty_weight: int = Field(default=20, ge=0, le=40, description="Additive risk penalty.")
    remediation_guidance: str = Field(default="", description="Actionable statutory compliance counsel.")
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0, description="NLP model confidence.")

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @property
    def matched_text(self) -> str:
        return self.context_snippet

    @property
    def remediation_advice(self) -> str:
        return self.remediation_guidance

    @property
    def weight(self) -> int:
        return self.penalty_weight


class MultiDimensionalRiskVector(BaseModel):
    """Orthogonal 4D risk vector decomposing regulatory exposure across distinct axes."""

    yield_risk: int = Field(..., ge=0, le=100, description="Velocity of promised yields and capital guarantees.")
    structural_risk: int = Field(..., ge=0, le=100, description="Multi-tier recruitment, binary MLM, Howey pooling.")
    liquidity_risk: int = Field(..., ge=0, le=100, description="Mandatory lock-ups, exit penalties, conditional liquidity.")
    legal_risk: int = Field(..., ge=0, le=100, description="Offshore secrecy havens, unilateral modification rights.")


class AuditAssessmentReport(BaseModel):
    """Comprehensive compliance assessment report synthesized by the evaluation engine."""

    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique audit trace identifier.")
    file_name: str = Field(..., description="Audited document filename.")
    suspicion_score: int = Field(..., ge=0, le=100, description="Bounded scalar score S in [0, 100].")
    risk_tier: RiskTier = Field(..., description="Governing risk tier classification.")
    risk_vector: MultiDimensionalRiskVector = Field(..., description="Decomposed 4D risk vector.")
    total_findings: int = Field(..., ge=0, description="Aggregate count of heuristic and semantic violations.")
    findings: List[Finding] = Field(default_factory=list, description="Granular heuristic rule infractions.")
    semantic_findings: List[Any] = Field(default_factory=list, description="Contextual NLP infractions.")
    executive_summary: str = Field(..., description="Executive compliance narrative verdict.")
    remediation_actions: List[str] = Field(default_factory=list, description="De-duplicated statutory remediation plan.")

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class ContractAuditRequest(BaseModel):
    """Inbound REST request schema for text compliance auditing."""

    content: str = Field(..., min_length=1, description="Raw contract text or promotional draft.")
    document_title: Optional[str] = Field(default="contract_draft.txt", description="Optional document label.")


# Universal Type Aliases for Backward & Forward Compatibility
ClauseFinding = Finding
RuleDefinition = RegulatoryRule
ComplianceFinding = Finding