"""Automated unit test suite verifying regex heuristic detection and text sanitization."""

from __future__ import annotations

from collections.abc import Callable

from src.domain.models import DocumentPayload
from src.engines.heuristic_scanner import HeuristicScanner
from src.ingestion.normalizer import TextNormalizer


def test_text_normalizer_collapses_obfuscation() -> None:
    """Verifies that TextNormalizer safely de-obfuscates spaced characters and numbers."""
    evasive_text = "Get g u a r a n t e e d 1 . 5 % d a i l y yields with 1 0 0 % safety."
    cleaned = TextNormalizer.normalize(evasive_text)

    assert "guaranteed" in cleaned
    assert "1.5%" in cleaned
    assert "daily" in cleaned
    assert "100%" in cleaned


def test_text_normalizer_handles_empty_input() -> None:
    """Verifies that TextNormalizer handles empty or whitespace-only strings gracefully."""
    assert TextNormalizer.normalize("") == ""
    assert TextNormalizer.normalize("   \n\t   ") == ""


def test_heuristic_scanner_handles_empty_payload(
    create_payload: Callable[[str, str], DocumentPayload],
) -> None:
    """Verifies that HeuristicScanner returns an empty finding list when payload text is blank."""
    payload = create_payload("", "empty.txt")
    scanner = HeuristicScanner()
    findings = scanner.scan(payload)

    assert findings == []


def test_heuristic_scanner_detects_predatory_hyip_clauses(
    predatory_hyip_contract: str,
    create_payload: Callable[[str, str], DocumentPayload],
) -> None:
    """Verifies complete detection coverage against high-yield Ponzi and MLM patterns."""
    payload = create_payload(predatory_hyip_contract, "predatory_hyip.txt")
    scanner = HeuristicScanner()
    findings = scanner.scan(payload)

    rule_ids = {f.rule_id for f in findings}

    # Tier 1 Critical Checks (+40 points each)
    assert "HYIP-001" in rule_ids, "Failed to flag guaranteed daily yield trap"
    assert "HOWEY-001" in rule_ids, "Failed to flag passive yield pooling syndicate"
    assert "PYR-001" in rule_ids, "Failed to flag downline/binary multi-tier commissions"

    # Tier 2 High Suspicion Checks (+20 points each)
    assert "LOCK-001" in rule_ids, "Failed to flag lockup exceeding 12 months"
    assert "LOCK-002" in rule_ids, "Failed to flag excessive early exit penalty"
    assert "UNFAIR-001" in rule_ids, "Failed to flag unilateral alteration clause"

    # Tier 3 Cautionary Checks (+10 points each)
    assert "JUR-001" in rule_ids, "Failed to flag offshore secrecy haven"


def test_heuristic_scanner_passes_legitimate_saas_contract(
    legitimate_saas_contract: str,
    create_payload: Callable[[str, str], DocumentPayload],
) -> None:
    """Verifies zero false positives on legitimate commercial software service contracts."""
    payload = create_payload(legitimate_saas_contract, "saas_contract.txt")
    scanner = HeuristicScanner()
    findings = scanner.scan(payload)

    assert len(findings) == 0, f"False positive detected: {[f.rule_id for f in findings]}"


def test_heuristic_scanner_catches_deobfuscated_clauses(
    obfuscated_scam_contract: str,
    create_payload: Callable[[str, str], DocumentPayload],
) -> None:
    """Verifies that combined normalization and scanning unmasks spaced evasion attempts."""
    payload = create_payload(obfuscated_scam_contract, "obfuscated_scam.txt")
    scanner = HeuristicScanner()
    findings = scanner.scan(payload)

    rule_ids = {f.rule_id for f in findings}
    assert "HYIP-001" in rule_ids
    assert "TECH-001" in rule_ids
    assert "LOCK-002" in rule_ids
    assert "JUR-001" in rule_ids
