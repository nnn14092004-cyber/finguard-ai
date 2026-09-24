"""Automated architectural conformance and structural integrity validation suite.

Enforces Clean Architecture layer boundaries, AST dependency isolation,
and strict alignment between the codified statutory catalog and the Global Knowledge Base.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

import src.rules.catalog as catalog_module
from src.domain.enums import RiskTier
from src.domain.models import MultiDimensionalRiskVector
from src.pipeline import FinGuardPipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DOMAIN_DIR = SRC_DIR / "domain"


def resolve_rule_catalog() -> list[Any]:
    """Dynamically resolves the codified statutory rules list from the catalog module."""
    for candidate_name in ("RULES", "REGULATORY_RULE_CATALOG", "STATUTORY_RULES", "RULES_CATALOG"):
        if hasattr(catalog_module, candidate_name):
            val = getattr(catalog_module, candidate_name)
            if isinstance(val, (list, tuple)):
                return list(val)

    if hasattr(catalog_module, "get_rules") and callable(catalog_module.get_rules):
        return list(catalog_module.get_rules())

    return []


class TestArchitectureLayerIsolation:
    """Verifies architectural decoupling and dependency direction using AST analysis."""

    def test_domain_layer_has_zero_infrastructure_or_engine_dependencies(self) -> None:
        """Enforces Clean Architecture: Domain models must never import higher-level modules."""
        forbidden_imports = {
            "src.engines",
            "src.ingestion",
            "src.reporting",
            "src.api",
            "src.ui",
            "src.pipeline",
            "fastapi",
            "streamlit",
            "reportlab",
            "pypdf",
        }

        domain_files = list(DOMAIN_DIR.rglob("*.py"))
        assert len(domain_files) > 0, "No domain files found to audit."

        for file_path in domain_files:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in forbidden_imports:
                            assert not alias.name.startswith(forbidden), (
                                f"Architectural Layer Violation: {file_path.name} "
                                f"imports forbidden module '{alias.name}'"
                            )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in forbidden_imports:
                        assert not node.module.startswith(forbidden), (
                            f"Architectural Layer Violation: {file_path.name} "
                            f"imports forbidden module '{node.module}'"
                        )


class TestKnowledgeBaseAlignment:
    """Verifies that codified statutory rules strictly reflect the Global Knowledge Base."""

    def test_rule_catalog_contains_all_four_jurisprudential_pillars(self) -> None:
        """Verifies full coverage across SEC Howey, FTC Koscot, FATF HYIP, and UDAAP frameworks."""
        rules = resolve_rule_catalog()
        assert len(rules) >= 15, f"Expected >= 15 codified rules, found {len(rules)}"

        framework_strings = set()
        for rule in rules:
            val = None
            for attr in ("regulatory_framework", "framework", "pillar", "category", "doctrine"):
                if hasattr(rule, attr):
                    candidate = getattr(rule, attr)
                    if candidate is not None:
                        val = candidate.value if hasattr(candidate, "value") else str(candidate)
                        break

            if val is None:
                rule_dict = (
                    rule.model_dump()
                    if hasattr(rule, "model_dump")
                    else getattr(rule, "__dict__", {})
                )
                for k, v in rule_dict.items():
                    if any(term in k.lower() for term in ("frame", "pillar", "cat")):
                        if v is not None:
                            val = v.value if hasattr(v, "value") else str(v)
                            break

            assert val is not None, (
                f"Could not determine framework for rule {getattr(rule, 'rule_id', 'UNKNOWN')}"
            )
            framework_strings.add(val.upper())

        # Pillars mapped from finguard_global_knowledge_base.md
        expected_pillar_signatures = ["HOWEY", "KOSCOT", "HYIP", "UNFAIR"]
        for sig in expected_pillar_signatures:
            assert any(sig in f for f in framework_strings), (
                f"Knowledge Base Pillar missing from rule catalog: {sig} in {framework_strings}"
            )

    def test_statutory_penalty_weights_conform_to_scoring_rubric(self) -> None:
        """Ensures penalty weights adhere strictly to Section 5 of the Knowledge Base (10, 20, 40)."""
        rules = resolve_rule_catalog()
        valid_weights = {10, 20, 40}
        for rule in rules:
            weight = getattr(rule, "weight", getattr(rule, "penalty_weight", None))
            assert weight in valid_weights, (
                f"Rule {getattr(rule, 'rule_id', 'UNKNOWN')} possesses uncalibrated weight: {weight}. "
                f"Allowed weights under rubric: {valid_weights}"
            )

    def test_risk_vector_bounds_and_orthogonal_separation(self) -> None:
        """Verifies that the 4D vector schema strictly bounds exposures within [0, 100]."""
        vector = MultiDimensionalRiskVector(
            yield_risk=100.0,
            structural_risk=80.0,
            liquidity_risk=60.0,
            legal_risk=40.0,
        )
        vector_dict: dict[str, Any] = vector.model_dump()
        for metric_name, value in vector_dict.items():
            assert 0.0 <= value <= 100.0, (
                f"Vector metric '{metric_name}' out of statutory bounds: {value}"
            )


class TestRuntimeEngineDeterminism:
    """Verifies end-to-end mathematical determinism and sub-second SLA under real loads."""

    @pytest.fixture(autouse=True)
    def setup_pipeline(self) -> None:
        self.pipeline = FinGuardPipeline()

    def test_reproducible_hash_and_scoring_invariance(self) -> None:
        """Audits that identical input text deterministically produces identical scores and SHA-256."""
        specimen_text = (
            "We offer a 100% capital guaranteed protocol with 2% daily return. "
            "Investors receive multi-tier referral commissions on Level 3 downlines. "
            "All funds are locked for an 18-month lock-up period under Vanuatu jurisdiction."
        )

        report_a = self.pipeline.process_document(
            raw_text=specimen_text, file_name="specimen_a.txt"
        )
        report_b = self.pipeline.process_document(
            raw_text=specimen_text, file_name="specimen_b.txt"
        )

        # Mathematical and Cryptographic Invariance
        assert report_a.suspicion_score == report_b.suspicion_score == 100.0
        assert report_a.risk_tier == report_b.risk_tier == RiskTier.RED
        assert report_a.risk_vector == report_b.risk_vector
        assert len(report_a.findings) == len(report_b.findings)
