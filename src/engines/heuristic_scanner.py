"""Deterministic Heuristic Scanner Engine for FinGuard-AI.

Scans normalized financial contract payloads against compiled regulatory regex rules,
extracting granular infringing clause findings and location spans.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional
from src.domain.models import ClauseFinding, DocumentPayload, Finding
from src.rules.catalog import RegulatoryCatalog, RegulatoryRule


class HeuristicScanner:
    """Engine executing deterministic pattern matching against codified regulatory rules."""

    def __init__(self, rules: Optional[List[RegulatoryRule]] = None) -> None:
        self.rules: List[RegulatoryRule] = (
            list(rules) if rules is not None else list(RegulatoryCatalog.get_rules())
        )

    def scan(self, payload: DocumentPayload) -> List[Finding]:
        """Scans contract payload text and returns all identified regulatory infractions."""
        findings: List[Finding] = []
        text: str = (
            getattr(payload, "normalized_content", None)
            or getattr(payload, "normalized_text", "")
            or ""
        )

        if not text or not text.strip():
            return findings

        for rule in self.rules:
            raw_pattern = str(rule.pattern)
            compiled_pattern = re.compile(raw_pattern, re.IGNORECASE)

            for match in compiled_pattern.finditer(text):
                findings.append(
                    Finding(
                        rule_id=rule.rule_id,
                        rule_name=rule.rule_name,
                        severity=rule.severity,
                        regulatory_framework=rule.regulatory_framework,
                        weight=rule.weight,
                        matched_text=match.group(0),
                        category=rule.category,
                        remediation_advice=rule.remediation_advice,
                        start_index=match.start(),
                        end_index=match.end(),
                    )
                )

        return findings