"""Automated verification suite executing FinGuardPipeline across historical case studies."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from src.pipeline import FinGuardPipeline

BASE_DIR = Path(__file__).resolve().parent.parent
CASES_DIR = BASE_DIR / "data" / "historical_cases"
MANIFEST_FILE = CASES_DIR / "historical_manifest.json"


def normalize_tier(tier_str: str) -> str:
    """Normalizes tier representations mapping RED and RED_FLAG into a canonical form."""
    cleaned = tier_str.strip().upper().replace(" ", "_")
    if cleaned in ("RED", "RED_FLAG"):
        return "RED_FLAG"
    return cleaned


def resolve_vector_component(vector: Any, *attr_names: str) -> int:
    """Defensively resolves integer risk component from schema across potential attribute aliases."""
    for attr in attr_names:
        if hasattr(vector, attr):
            val = getattr(vector, attr)
            if isinstance(val, (int, float)):
                return int(val)
    return 0


def main() -> None:
    """Executes audits against all historical cases and validates regulatory assertions."""
    if not MANIFEST_FILE.exists():
        print(f"ERROR: Manifest not found at {MANIFEST_FILE}. Run generate_historical_case_studies.py first.")
        return

    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    pipeline = FinGuardPipeline()

    print("\n" + "=" * 95)
    print(f"| {'FINGUARD-AI REAL-WORLD HISTORICAL AUDIT BENCHMARK':^91} |")
    print("=" * 95)
    print(
        f"| {'Case ID':<22} | {'Expected':<10} | {'Actual Tier':<12} | {'Score':<7} | {'Latency':<9} | {'Status':<14} |"
    )
    print("-" * 95)

    all_passed = True

    for item in manifest:
        file_path = CASES_DIR / item["file_name"]
        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}")
            all_passed = False
            continue

        content = file_path.read_text(encoding="utf-8")

        # High-precision hardware timer
        t0 = time.perf_counter()
        report = pipeline.process_document(raw_text=content, file_name=item["file_name"])
        latency_ms = (time.perf_counter() - t0) * 1000.0

        raw_actual_tier = (
            report.risk_tier.value
            if hasattr(report.risk_tier, "value")
            else str(report.risk_tier)
        )
        expected_tier = str(item["expected_tier"])

        norm_actual = normalize_tier(raw_actual_tier)
        norm_expected = normalize_tier(expected_tier)

        tier_match = norm_actual == norm_expected
        if not tier_match:
            all_passed = False

        status_label = "PASSED" if tier_match else "FAILED (MISMATCH)"

        print(
            f"| {item['case_id']:<22} | "
            f"{expected_tier:<10} | "
            f"{raw_actual_tier:<12} | "
            f"{report.suspicion_score:<7} | "
            f"{latency_ms:<6.2f} ms | "
            f"{status_label:<14} |"
        )

        # Print rule detection details and 4D risk vector
        if report.findings:
            triggered_rules = {f.rule_id for f in report.findings}
            v = report.risk_vector
            y_risk = resolve_vector_component(v, "yield_risk", "yield_velocity_risk")
            s_risk = resolve_vector_component(v, "structural_risk", "structural_pyramid_risk")
            l_risk = resolve_vector_component(v, "liquidity_risk", "liquidity_lockup_risk")
            j_risk = resolve_vector_component(v, "legal_risk", "regulatory_evasion_risk")

            print(f"  --> Triggered Infractions: {', '.join(sorted(triggered_rules))}")
            print(
                f"  --> Risk Vector: [Yield: {y_risk}%, Structural: {s_risk}%, "
                f"Liquidity: {l_risk}%, Legal: {j_risk}%]"
            )
        print("-" * 95)

    print("=" * 95)
    if all_passed:
        print("[VERDICT] ALL HISTORICAL BENCHMARKS VALIDATED WITH 100% REGULATORY ACCURACY.")
    else:
        print("[VERDICT] REGRESSION IDENTIFIED IN HISTORICAL BENCHMARKS. REVIEW RULE CALIBRATION.")
    print("=" * 95 + "\n")


if __name__ == "__main__":
    main()