"""Unit test suite verifying court-admissible forensic PDF dossier generation."""

from __future__ import annotations

from pathlib import Path

from src.pipeline import FinGuardPipeline
from src.reporting.pdf_generator import ForensicReportGenerator


def test_forensic_report_generator_produces_valid_pdf_bytes() -> None:
    """Verifies that ForensicReportGenerator produces non-empty valid PDF byte streams."""
    pipeline = FinGuardPipeline()
    sample_scam = (
        "We guarantee a 2.5% daily return with 100% capital guaranteed. "
        "Earn 10% matching downline referral commission across binary legs. "
        "Mandatory 18-month lock-up period applies. Early withdrawal penalty fee strips 40%."
    )
    report = pipeline.process_document(raw_text=sample_scam, file_name="sample_scam.txt")

    generator = ForensicReportGenerator()
    pdf_bytes = generator.generate_pdf_bytes(report)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF documents begin with magic byte header '%PDF-'
    assert pdf_bytes.startswith(b"%PDF-")


def test_forensic_report_generator_writes_file_to_disk(tmp_path: Path) -> None:
    """Verifies that PDF dossier file can be successfully compiled and written to disk."""
    pipeline = FinGuardPipeline()
    sample_clean = "Standard software subscription agreement governed by the State of Delaware."
    report = pipeline.process_document(raw_text=sample_clean, file_name="saas_sla.txt")

    generator = ForensicReportGenerator()
    output_pdf = tmp_path / "audit_dossier.pdf"
    result_path = generator.generate_pdf_file(report, output_pdf)

    assert result_path.is_file()
    assert result_path.stat().st_size > 1000
