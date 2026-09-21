"""Heuristic Regular Expression Scanner for FinGuard-AI.

Executes deterministic pattern scanning across normalized contract text
to identify explicit violations of international financial regulations (FATF, SEC Howey, FTC Koscot).
"""

from __future__ import annotations

import re
from typing import List, Pattern

from src.domain.models import ClauseFinding, DocumentPayload, RuleDefinition
from src.rules.catalog import RegulatoryCatalog


class HeuristicScanner:
    """Deterministic pattern matching engine for codified regulatory rules."""

    def __init__(self) -> None:
        """Initializes the scanner with precompiled regulatory rules."""
        self._rules: List[RuleDefinition] = RegulatoryCatalog.get_rules()

    def scan(self, payload: DocumentPayload) -> List[ClauseFinding]:
        """Scans the normalized content of a document payload for predatory patterns.

        Args:
            payload: Preprocessed document container holding normalized content.

        Returns:
            List[ClauseFinding]: Collection of all identified violations and clause matches.
        """
        findings: List[ClauseFinding] = []
        text: str = payload.normalized_content

        if not text or not text.strip():
            return findings

        for rule in self._rules:
            # Defensive compilation resolves both precompiled regex objects and raw strings
            pattern: Pattern[str] = (
                rule.pattern
                if hasattr(rule.pattern, "finditer")
                else re.compile(str(rule.pattern), re.IGNORECASE)
            )

            for match in pattern.finditer(text):
                findings.append(
                    ClauseFinding(
                        rule_id=rule.rule_id,
                        rule_name=rule.rule_name,
                        severity=rule.severity,
                        weight=rule.weight,
                        category=rule.category,
                        matched_text=match.group(0),
                        start_index=match.start(),
                        end_index=match.end(),
                        regulatory_framework=rule.regulatory_framework,
                        remediation_advice=rule.remediation_advice,
                    )
                )

        return findings