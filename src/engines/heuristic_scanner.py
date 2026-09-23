"""Deterministic regex scanner executing statutory pattern evaluation."""

from __future__ import annotations

import re

from src.domain.models import DocumentPayload, Finding
from src.rules.catalog import RegulatoryRule, get_catalog


class HeuristicScanner:
    """Pre-compiled statutory regular expression inspection engine."""

    def __init__(self, rules: list[RegulatoryRule] | None = None) -> None:
        """Initializes scanner with cached pre-compiled regex automata."""
        self.rules: list[RegulatoryRule] = (
            list(rules) if rules is not None else get_catalog().get_rules()
        )
        self._compiled_patterns: list[tuple[RegulatoryRule, list[re.Pattern[str]]]] = [
            (rule, [re.compile(p, re.IGNORECASE) for p in rule.patterns])
            for rule in self.rules
        ]

    def scan(self, payload: DocumentPayload) -> list[Finding]:
        """Scans ingested contract payload against codified statutory patterns."""
        target_text = payload.normalized_text or payload.raw_text
        if not target_text or not target_text.strip():
            return []

        findings: list[Finding] = []
        for rule, patterns in self._compiled_patterns:
            for pattern in patterns:
                for match in pattern.finditer(target_text):
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
