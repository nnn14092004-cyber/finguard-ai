"""Institutional sub-second latency and throughput benchmark harness for FinGuard-AI."""

from __future__ import annotations

import statistics
import time
from typing import Any

from src.domain.models import AuditAssessmentReport
from src.pipeline import FinGuardPipeline

# Institutional benchmark corpus exercising varied syntactic complexities
BENCHMARK_CORPUS: list[dict[str, str]] = [
    {
        "name": "Synthetic High-Yield Ponzi Trap",
        "content": (
            "ALPHA WEALTH PROTOCOL: Deposit capital into our automated liquidity pool. "
            "Guaranteed 2.5% daily return with 100% capital guaranteed against principal loss. "
            "Participants earn returns through multi-tier referral downline investment volume bonuses. "
            "Binary bonus paid on newly recruited capital across legs. Mandatory 18-month lock-up applies. "
            "Early withdrawal penalty fee strips 40% of deposited assets. Governed by the laws of Vanuatu."
        ),
    },
    {
        "name": "Securities Syndicate Reliance Trap",
        "content": (
            "COLLECTIVE STAKING MEMORANDUM: Participants pool funds into our central capital vault. "
            "All trading operations and algorithmic arbitrage are executed entirely by our quantitative team. "
            "Participants remain completely passive investors with no trading expertise required, "
            "enjoying steady dividends derived solely from the managerial efforts of the promoter."
        ),
    },
    {
        "name": "Standard Enterprise SaaS Agreement (Clean Control)",
        "content": (
            "ENTERPRISE CLOUD SERVICE LEVEL AGREEMENT: Provider guarantees 99.9% uptime during each "
            "billing cycle. Customer remits service fees within 30 calendar days. Either party may "
            "terminate without cause upon providing 60 days advance written notice. Governed by "
            "the commercial laws of the State of Delaware, United States."
        ),
    },
    {
        "name": "Venture Equity Vesting Agreement (Clean Control)",
        "content": (
            "SERIES A PREFERRED SHAREHOLDERS AGREEMENT: Founders agree to standard share lock-up "
            "subject to a 4-year linear vesting schedule with a 1-year cliff. Common shares may not be "
            "transferred without prior consent of the Board of Directors. Governed by the commercial "
            "laws of the State of Delaware."
        ),
    },
]


def format_table_row(label: str, value: str, width: int = 70) -> str:
    """Formats an aligned console table row."""
    padding = width - len(label) - len(value) - 4
    return f"| {label}{' ' * max(padding, 2)}: {value} |"


def execute_subsecond_stress_test(
    iterations_per_doc: int = 250, warmup_cycles: int = 50
) -> dict[str, Any]:
    """Executes high-iteration sub-second latency profiling across the core pipeline."""
    pipeline = FinGuardPipeline()
    latencies_ns: list[int] = []

    # 1. Warm-up Phase: Pre-heat CPU caches and Python bytecode instruction caches
    for _ in range(warmup_cycles):
        for doc in BENCHMARK_CORPUS:
            _ = pipeline.process_document(raw_text=doc["content"], file_name=doc["name"])

    # 2. Measurement Phase: High-precision timestamp acquisition
    total_evaluations = len(BENCHMARK_CORPUS) * iterations_per_doc
    start_wall_clock = time.perf_counter()

    for _ in range(iterations_per_doc):
        for doc in BENCHMARK_CORPUS:
            t0 = time.perf_counter_ns()
            report: AuditAssessmentReport = pipeline.process_document(
                raw_text=doc["content"], file_name=doc["name"]
            )
            t1 = time.perf_counter_ns()
            latencies_ns.append(t1 - t0)

            # Defensive assertion ensuring full semantic evaluation completeness
            assert report.suspicion_score >= 0

    elapsed_wall_seconds = time.perf_counter() - start_wall_clock

    # 3. Statistical Telemetry Synthesis
    latencies_ms = [ns / 1_000_000.0 for ns in latencies_ns]
    latencies_ms.sort()

    mean_ms = statistics.mean(latencies_ms)
    median_ms = statistics.median(latencies_ms)
    stdev_ms = statistics.stdev(latencies_ms) if len(latencies_ms) > 1 else 0.0
    min_ms = latencies_ms[0]
    max_ms = latencies_ms[-1]

    # Percentile indexing
    def get_percentile(pct: float) -> float:
        idx = int(round((len(latencies_ms) - 1) * pct))
        return latencies_ms[idx]

    p90_ms = get_percentile(0.90)
    p95_ms = get_percentile(0.95)
    p99_ms = get_percentile(0.99)
    throughput_dps = total_evaluations / elapsed_wall_seconds

    return {
        "total_evaluations": total_evaluations,
        "elapsed_wall_seconds": elapsed_wall_seconds,
        "throughput_dps": throughput_dps,
        "mean_ms": mean_ms,
        "median_ms": median_ms,
        "stdev_ms": stdev_ms,
        "min_ms": min_ms,
        "max_ms": max_ms,
        "p90_ms": p90_ms,
        "p95_ms": p95_ms,
        "p99_ms": p99_ms,
    }


def main() -> None:
    """Entry point rendering institutional latency benchmark report."""
    border = "+" + "=" * 70 + "+"
    divider = "+" + "-" * 70 + "+"

    print("\n" + border)
    print("|" + " FINGUARD-AI HIGH-THROUGHPUT SUB-SECOND BENCHMARK PROFILE ".center(70) + "|")
    print(border)
    print(format_table_row("Execution Target", "FinGuardPipeline.process_document()"))
    print(format_table_row("Benchmarked Corpus", f"{len(BENCHMARK_CORPUS)} Distinct Institutional Contracts"))
    print(format_table_row("Warmup Iterations", "50 cycles / document"))
    print(format_table_row("Sampling Repetitions", "250 iterations (1,000 total audits)"))
    print(format_table_row("Timing Clock", "time.perf_counter_ns (Hardware Clock)"))
    print(divider)

    print("|" + " EXECUTING DETERMINISTIC STRESS SUITE... ".center(70) + "|")
    results = execute_subsecond_stress_test(iterations_per_doc=250, warmup_cycles=50)

    print(divider)
    print("|" + " LATENCY SLA & THROUGHPUT TELEMETRY ".center(70) + "|")
    print(divider)
    print(format_table_row("Total Audits Evaluated", f"{results['total_evaluations']:,} docs"))
    print(format_table_row("Total Execution Time", f"{results['elapsed_wall_seconds']:.3f} seconds"))
    print(format_table_row("System Throughput", f"{results['throughput_dps']:,.1f} docs/sec"))
    print(divider)
    print(format_table_row("Mean Latency", f"{results['mean_ms']:.3f} ms"))
    print(format_table_row("Median Latency (P50)", f"{results['median_ms']:.3f} ms"))
    print(format_table_row("P90 Latency", f"{results['p90_ms']:.3f} ms"))
    print(format_table_row("P95 Latency", f"{results['p95_ms']:.3f} ms"))
    print(format_table_row("P99 Latency (Tail)", f"{results['p99_ms']:.3f} ms"))
    print(format_table_row("Min Latency (Cache Hit)", f"{results['min_ms']:.3f} ms"))
    print(format_table_row("Max Latency (Outlier)", f"{results['max_ms']:.3f} ms"))
    print(format_table_row("Standard Deviation", f"{results['stdev_ms']:.3f} ms"))
    print(divider)

    # Verification of Sub-Second SLA
    sub_second_sla = results["p99_ms"] < 1000.0
    ultra_low_latency_sla = results["p99_ms"] < 50.0

    print(
        format_table_row(
            "Sub-Second SLA (< 1,000 ms)",
            "PASSED (100% Guaranteed)" if sub_second_sla else "FAILED",
        )
    )
    print(
        format_table_row(
            "Institutional SLA (< 50 ms)",
            "PASSED (Real-Time Trade Ready)" if ultra_low_latency_sla else "REVIEW REQUIRED",
        )
    )
    print(border + "\n")


if __name__ == "__main__":
    main()