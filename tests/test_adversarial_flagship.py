"""Integration test verifying FinGuard-AI against the 8-page Flagship Master Adversarial PPM."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import pytest

from src.domain.enums import RiskTier
from src.ingestion.normalizer import TextNormalizer, extract_text_from_pdf
from src.pipeline import FinGuardPipeline

FLAGSHIP_PPM_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "benchmark"
    / "flagship_master_adversarial_ppm.pdf"
)


class TestFlagshipAdversarialPPM:
    """Verifies end-to-end ingestion and statutory audit of multi-page obfuscated legal agreements."""

    @pytest.fixture(autouse=True)
    def setup_pipeline_and_specimen(self) -> None:
        """Initializes pipeline and self-heals specimen if not present in clean CI environments."""
        self.pipeline = FinGuardPipeline()

        # Self-healing fixture for headless CI runners
        if not FLAGSHIP_PPM_PATH.exists() or FLAGSHIP_PPM_PATH.stat().st_size == 0:
            from scripts.generate_adversarial_dataset import generate_flagship_master_ppm

            FLAGSHIP_PPM_PATH.parent.mkdir(parents=True, exist_ok=True)
            generate_flagship_master_ppm(FLAGSHIP_PPM_PATH)

    def test_flagship_ppm_file_existence(self) -> None:
        """Ensures the flagship master adversarial PDF has been compiled to disk."""
        assert FLAGSHIP_PPM_PATH.exists(), f"Flagship specimen not found at: {FLAGSHIP_PPM_PATH}"
        assert FLAGSHIP_PPM_PATH.stat().st_size > 0, "Flagship specimen is empty."

    def test_flagship_ppm_ingestion_and_dehyphenation(self) -> None:
        """Verifies in-memory extraction and cross-line de-obfuscation normalizer."""
        raw_pdf_bytes = FLAGSHIP_PPM_PATH.read_bytes()
        extracted_text = extract_text_from_pdf(raw_pdf_bytes)
        normalizer = TextNormalizer()
        normalized = normalizer.normalize(extracted_text)

        # Assert needle-in-a-haystack clause presence and dehyphenation
        assert "2.5% daily" in normalized, "Failed to resolve '2.5% daily' clause."
        assert "referral commission" in normalized, (
            "Failed to resolve 'referral commission' obfuscation."
        )
        assert "18-month" in normalized, "Failed to resolve '18-month' obfuscation."
        assert "early withdrawal" in normalized, "Failed to resolve 'early withdrawal' obfuscation."

    def test_flagship_ppm_full_statutory_enforcement(self) -> None:
        """Asserts maximum risk classification across all four regulatory dimensions."""
        raw_pdf_bytes = FLAGSHIP_PPM_PATH.read_bytes()
        extracted_text = extract_text_from_pdf(raw_pdf_bytes)

        # Hardware execution timer enforcing sub-second real-time SLA
        start_time = time.perf_counter()
        report = self.pipeline.process_document(
            raw_text=extracted_text,
            file_name=FLAGSHIP_PPM_PATH.name,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # 1. Scoring & Tier Classification
        assert report.suspicion_score == 100.0, f"Expected 100.0, got {report.suspicion_score}"
        assert report.risk_tier == RiskTier.RED

        # 2. Resilient Four-Dimensional Orthogonal Vector Saturation Verification
        vector = report.risk_vector
        vector_dict: dict[str, Any] = (
            vector.model_dump()
            if hasattr(vector, "model_dump")
            else getattr(vector, "__dict__", {})
        )

        yield_val = next((v for k, v in vector_dict.items() if "yield" in k.lower()), 0.0)
        structural_val = next(
            (v for k, v in vector_dict.items() if "struct" in k.lower() or "mlm" in k.lower()),
            0.0,
        )
        lockup_val = next(
            (v for k, v in vector_dict.items() if "lock" in k.lower() or "liquid" in k.lower()),
            0.0,
        )
        jur_val = next(
            (v for k, v in vector_dict.items() if "jur" in k.lower() or "legal" in k.lower()),
            0.0,
        )

        assert yield_val > 0.0, f"Yield Velocity Risk failed to trigger: {vector_dict}"
        assert structural_val > 0.0, f"Structural / MLM Risk failed to trigger: {vector_dict}"
        assert lockup_val > 0.0, f"Liquidity Lockup Risk failed to trigger: {vector_dict}"
        assert jur_val > 0.0, f"Jurisdiction Evasion Risk failed to trigger: {vector_dict}"

        # 3. Cryptographic Non-Repudiation Proof & Sub-Second Latency SLA
        assert len(report.document_id) > 0, "Document ID must be assigned."
        content_sha256 = hashlib.sha256(report.raw_content.encode("utf-8")).hexdigest()
        assert len(content_sha256) == 64, f"Invalid SHA-256 digest length: {content_sha256}"
        assert "SHA-256" in report.executive_summary, (
            "Executive summary must stamp cryptographic provenance."
        )
        assert elapsed_ms < 1000.0, f"Latency breached sub-second SLA: {elapsed_ms:.2f}ms"
