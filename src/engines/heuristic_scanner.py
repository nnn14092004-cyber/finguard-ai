"""Deterministic regex scanning engine for codified regulatory rules."""

from __future__ import annotations

import re
from typing import List, Optional
from src.domain.models import DocumentPayload, Finding
from src.rules.catalog import RegulatoryCatalog, RegulatoryRule


class HeuristicScanner:
    """Scans text payloads against compiled regulatory regex patterns."""

    def __init__(self, rules: Optional[List[RegulatoryRule]] = None) -> None:
        if rules is not None:
            self.rules: List[RegulatoryRule] = list(rules)
        else:
            self.rules: List[RegulatoryRule] = list(RegulatoryCatalog.get_rules())

    def scan(self, payload: DocumentPayload) -> List[Finding]:
        """Executes regex pattern matching against document text.

        Args:
            payload: Normalized document payload container.

        Returns:
            List of identified compliance findings.
        """
        findings: List[Finding] = []
        text: str = payload.normalized_content or payload.normalized_text

        if not text.strip():
            return findings

        for rule in self.rules:
            pattern = re.compile(rule.pattern, re.IGNORECASE)
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