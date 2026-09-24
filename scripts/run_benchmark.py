"""Automated adversarial stress-test benchmark runner for FinGuard-AI."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from src.ingestion.normalizer import extract_text_from_pdf
from src.pipeline import FinGuardPipeline

BENCHMARK_DIR = Path("data/benchmark")
GROUND_TRUTH_PATH = BENCHMARK_DIR / "ground_truth.json"
RESULTS_PATH = Path("benchmark_results.json")


def run_benchmark() -> None:
    """Executes end-to-end performance and accuracy evaluation across all 100 benchmark PDFs."""
    if not GROUND_TRUTH_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {GROUND_TRUTH_PATH}. Run generate_adversarial_dataset.py first."
        )

    with open(GROUND_TRUTH_PATH, encoding="utf-8") as f:
        ground_truth: dict[str, Any] = json.load(f)

    pipeline = FinGuardPipeline()

    tp = 0  # True Positives: Scam correctly flagged RED (score >= 75)
    fp = 0  # False Positives: Clean contract erroneously flagged high/red
    tn = 0  # True Negatives: Clean contract correctly classified GREEN (< 25)
    fn = 0  # False Negatives: Scam missed (< 75)

    latencies: list[float] = []
    audit_records: list[dict[str, Any]] = []

    print("\n" + "=" * 80)
    print("FINGUARD-AI INSTITUTIONAL BENCHMARK EXECUTION (100 ADVERSARIAL PDF CONTRACTS)")
    print("=" * 80 + "\n")

    for filename, expected in ground_truth.items():
        pdf_path = BENCHMARK_DIR / filename
        start_time = time.perf_counter()

        # Step 1: Ingestion & Text Extraction
        raw_text = extract_text_from_pdf(pdf_path)

        # Step 2: Full Audit Pipeline Execution
        report = pipeline.process_document(text=raw_text, file_name=filename)
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        latencies.append(duration_ms)

        score = report.suspicion_score
        is_scam = expected["is_adversarial"]

        # Classification verification against statutory thresholds
        if is_scam:
            if score >= 75:
                tp += 1
                status = "PASS (TP)"
            else:
                fn += 1
                status = f"FAIL (FN) - Score: {score}"
        else:
            if score < 25:
                tn += 1
                status = "PASS (TN)"
            else:
                fp += 1
                status = f"FAIL (FP) - Score: {score}"

        audit_records.append(
            {
                "file_name": filename,
                "expected_category": expected["category"],
                "score": score,
                "risk_tier": report.risk_tier.value,
                "latency_ms": round(duration_ms, 2),
                "status": status,
            }
        )
        print(f"[{status:<12}] {filename} -> Score: {score:>3}/100 in {duration_ms:>6.2f} ms")

    total_docs = len(ground_truth)
    total_time_s = sum(latencies) / 1000.0
    avg_latency_ms = sum(latencies) / total_docs
    p95_latency_ms = sorted(latencies)[int(total_docs * 0.95)]

    precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
    accuracy = ((tp + tn) / total_docs) * 100.0
    fpr = (fp / (fp + tn)) * 100.0 if (fp + tn) > 0 else 0.0

    print("\n" + "=" * 80)
    print("INSTITUTIONAL AUDIT BENCHMARK SUMMARY REPORT")
    print("=" * 80)
    print(
        f"Total Documents Tested     : {total_docs} files (80 Adversarial Traps, 20 Clean Controls)"
    )
    print(f"Total Processing Time      : {total_time_s:.2f} seconds")
    print(f"Average Latency / Document : {avg_latency_ms:.2f} ms (Target: < 500 ms)")
    print(f"P95 Processing Latency     : {p95_latency_ms:.2f} ms")
    print("-" * 80)
    print(f"True Positives (TP)        : {tp} / 80")
    print(f"True Negatives (TN)        : {tn} / 20")
    print(f"False Positives (FP)       : {fp} / 20 (Target: 0)")
    print(f"False Negatives (FN)       : {fn} / 80 (Target: 0)")
    print("-" * 80)
    print(f"Recall (Sensitivity)       : {recall:.2f}% (Target: 100.0%)")
    print(f"Precision                  : {precision:.2f}% (Target: 100.0%)")
    print(f"Accuracy                   : {accuracy:.2f}%")
    print(f"False Positive Rate (FPR)  : {fpr:.2f}% (Target: 0.0%)")
    print("=" * 80 + "\n")

    benchmark_summary = {
        "metrics": {
            "total_documents": total_docs,
            "precision_pct": round(precision, 2),
            "recall_pct": round(recall, 2),
            "accuracy_pct": round(accuracy, 2),
            "false_positive_rate_pct": round(fpr, 2),
            "avg_latency_ms": round(avg_latency_ms, 2),
            "p95_latency_ms": round(p95_latency_ms, 2),
        },
        "records": audit_records,
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)

    print(f"Full benchmark dossier saved to {RESULTS_PATH.resolve()}")


if __name__ == "__main__":
    run_benchmark()
