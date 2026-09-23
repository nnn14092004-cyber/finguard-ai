"""Deterministic regex scanning engine for codified regulatory rules."""

from __future__ import annotations

import re
from typing import List, Optional, Pattern, Tuple

from src.domain.models import DocumentPayload, Finding
from src.rules.catalog import RegulatoryCatalog, RegulatoryRule


class HeuristicScanner:
    """Scans text payloads against pre-compiled regulatory regex patterns."""

    def __init__(self, rules: Optional[List[RegulatoryRule]] = None) -> None:
        """Initializes scanner and pre-compiles regex patterns for low-latency execution."""
        if rules is not None:
            self.rules: List[RegulatoryRule] = list(rules)
        else:
            self.rules: List[RegulatoryRule] = list(RegulatoryCatalog.get_rules())

        # Pre-compile regex patterns during initialization to preserve < 0.45s latency benchmark
        self._compiled_rules: List[Tuple[RegulatoryRule, Pattern[str]]] = [
            (
                rule,
                rule.pattern
                if isinstance(rule.pattern, re.Pattern)
                else re.compile(rule.pattern, re.IGNORECASE),
            )
            for rule in self.rules
        ]

    def scan(self, payload: DocumentPayload) -> List[Finding]:
        """Executes regex pattern matching against document text.

        Args:
            payload: Normalized document payload container.

        Returns:
            List of identified compliance findings.
        """
        findings: List[Finding] = []
        text: str = (
            getattr(payload, "normalized_content", None)
            or getattr(payload, "normalized_text", "")
            or ""
        )

        if not text.strip():
            return findings

        for rule, pattern in self._compiled_rules:
            for match in pattern.finditer(text):
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