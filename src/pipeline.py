"""Orchestration pipeline integrating ingestion, heuristic, semantic, and scoring engines."""

from __future__ import annotations

import logging
import uuid

from src.domain.models import AuditAssessmentReport, DocumentPayload
from src.engines.heuristic_scanner import HeuristicScanner
from src.engines.scoring_engine import ScoringEngine
from src.engines.semantic_auditor import SemanticAuditor
from src.ingestion.normalizer import TextNormalizer

logger = logging.getLogger("finguard.pipeline")


class FinGuardPipeline:
    """Unified compliance audit pipeline executing multi-layered regulatory assessment."""

    def __init__(self) -> None:
        """Initializes internal evaluation engines and text processing automata."""
        self.normalizer = TextNormalizer()
        self.heuristic_scanner = HeuristicScanner()
        self.semantic_auditor = SemanticAuditor()
        self.scoring_engine = ScoringEngine()

    def audit_text(
        self,
        text: str = "",
        raw_text: str | None = None,
        document_id: str | None = None,
        file_name: str = "document.txt",
    ) -> AuditAssessmentReport:
        """Executes full compliance audit workflow over provided contract text."""
        resolved_text = raw_text if raw_text is not None else text
        doc_id = document_id or str(uuid.uuid4())
        normalized_text = self.normalizer.normalize(resolved_text)

        payload = DocumentPayload(
            document_id=doc_id,
            file_name=file_name,
            raw_text=resolved_text,
            raw_content=resolved_text,
            normalized_text=normalized_text,
            normalized_content=normalized_text,
        )

        heuristic_findings = self.heuristic_scanner.scan(payload)
        semantic_findings = self.semantic_auditor.audit(payload)

        report = self.scoring_engine.synthesize_assessment(
            payload=payload,
            heuristic_findings=heuristic_findings,
            semantic_findings=semantic_findings,
        )

        return report

    def process_document(
        self,
        text: str | None = None,
        raw_text: str | None = None,
        content: str | None = None,
        document_id: str | None = None,
        file_name: str = "document.txt",
    ) -> AuditAssessmentReport:
        """Universal compatibility facade executing document audit across variant parameter names."""
        resolved_text = (
            raw_text if raw_text is not None else (text if text is not None else (content or ""))
        )
        return self.audit_text(
            text=resolved_text,
            document_id=document_id,
            file_name=file_name,
        )
