"""Unit tests verifying PDF document ingestion, text extraction, and dehyphenation."""

from __future__ import annotations

import io

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate

from src.ingestion.normalizer import TextNormalizer, extract_text_from_pdf


def _create_sample_pdf(pages: list[str]) -> bytes:
    """Generates an in-memory PDF byte stream from list of page strings."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for idx, page_content in enumerate(pages):
        story.append(Paragraph(page_content, styles["Normal"]))
        if idx < len(pages) - 1:
            story.append(PageBreak())
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def test_extract_text_from_pdf_multi_page() -> None:
    """Verifies that multi-page PDF content is extracted and preserved."""
    pdf_bytes = _create_sample_pdf(
        ["Page 1: Terms of Agreement.", "Page 2: Execution and Signatures."]
    )
    text = extract_text_from_pdf(pdf_bytes)
    assert "Page 1: Terms of Agreement." in text
    assert "Page 2: Execution and Signatures." in text


def test_extract_text_from_pdf_empty_raises_or_returns_blank() -> None:
    """Verifies defensive handling of empty byte stream."""
    assert extract_text_from_pdf(b"") == ""


def test_text_normalizer_dehyphenates_cross_line_splits() -> None:
    """Verifies dehyphenation of cross-line and cross-page words."""
    normalizer = TextNormalizer()
    split_text = "Mandatory 18-\nmonth lock-up period applies with early\nwithdrawal penalties."
    normalized = normalizer.normalize(split_text)
    assert "18-month" in normalized
    assert "early withdrawal" in normalized
