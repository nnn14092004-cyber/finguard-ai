"""Master Orchestration Pipeline for FinGuard-AI.

Coordinates document ingestion, anti-obfuscation text normalization,
heuristic regular expression scanning, semantic contextual audit, and
multi-dimensional hybrid risk scoring.
"""

from __future__ import annotations

import uuid
from src.domain.models import AuditAssessmentReport, DocumentPayload
from src.engines.heuristic_scanner import HeuristicScanner
from src.engines.scoring_engine import ScoringEngine
from src.engines.semantic_auditor import SemanticAuditor
from src.ingestion.normalizer import TextNormalizer


class FinGuardPipeline:
    """Enterprise end-to-end regulatory compliance audit pipeline."""

    def __init__(self) -> None:
        """Initializes scanner, semantic auditor, and scoring sub-engines."""
        self._heuristic_scanner = HeuristicScanner()
        self._semantic_auditor = SemanticAuditor()

    def process_document(
        self,
        raw_text: str,
        file_name: str = "document.txt",
    ) -> AuditAssessmentReport:
        """Executes the complete audit pipeline against raw document text.

        Args:
            raw_text: Raw plain text extracted from financial agreement or promotion.
            file_name: Source document identifier.

        Returns:
            AuditAssessmentReport: Consolidated executive compliance and risk report.
        """
        # Step 1: Ingestion & Anti-Obfuscation Normalization
        normalized_text = TextNormalizer.normalize(raw_text or "")
        payload = DocumentPayload(
            document_id=str(uuid.uuid4()),
            file_name=file_name or "document.txt",
            raw_content=raw_text or "",
            normalized_content=normalized_text,
            character_count=len(normalized_text),
        )

        # Defensive short-circuit for blank / whitespace inputs
        if not normalized_text.strip():
            return ScoringEngine.evaluate(
                payload=payload,
                heuristic_findings=[],
                semantic_findings=[],
            )

        # Step 2: Deterministic Heuristic Regex Scanning
        heuristic_findings = self._heuristic_scanner.scan(payload)

        # Step 3: Contextual Semantic Audit (Phase 3)
        semantic_findings = self._semantic_auditor.audit(payload)

        # Step 4: Multi-Dimensional Hybrid Risk Scoring & Synthesis
        report = ScoringEngine.evaluate(
            payload=payload,
            heuristic_findings=heuristic_findings,
            semantic_findings=semantic_findings,
        )

        return report