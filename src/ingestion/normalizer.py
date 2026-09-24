"""Text sanitization, normalization, and PDF ingestion pipeline for FinGuard-AI.

Removes deliberate spacing tricks, leetspeak anomalies, cross-line hyphenations,
and extracts clean textual data from in-memory PDF binary streams.
"""

from __future__ import annotations

import io
import re
import unicodedata
from pathlib import Path
from typing import Final

from pypdf import PdfReader


def extract_text_from_pdf(file_source: bytes | str | Path) -> str:
    """Extracts raw textual disclosures from a PDF binary stream or file path.

    Args:
        file_source: In-memory byte buffer, file path string, or Path object.

    Returns:
        str: Concatenated, extracted raw text content across all document pages.

    Raises:
        ValueError: If file source is empty, unreadable, or contains corrupted PDF data.
    """
    if isinstance(file_source, bytes):
        if not file_source or not file_source.strip():
            return ""
        stream = io.BytesIO(file_source)
    elif isinstance(file_source, (str, Path)):
        path = Path(file_source)
        if not path.is_file() or path.stat().st_size == 0:
            return ""
        stream = io.BytesIO(path.read_bytes())
    else:
        raise ValueError(f"Unsupported file source type: {type(file_source)}")

    try:
        reader = PdfReader(stream)
        extracted_pages: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)
        return "\n\n".join(extracted_pages)
    except Exception as exc:
        raise ValueError(f"Failed to parse PDF document stream: {exc}") from exc


class TextNormalizer:
    """Sanitizes, unescapes, and de-obfuscates text extracted from investment agreements."""

    # Matches single-character spacing within a word: e.g., 'g u a r a n t e e d' -> 'guaranteed'
    _SPACED_LETTERS_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?<=\b[a-zA-Z]) (?=[a-zA-Z]\b)")

    # Matches spaced percentage/number patterns: e.g., '1 0 0 %' -> '100%', '1 . 5 %' -> '1.5%'
    _SPACED_NUMBERS_PATTERN: Final[re.Pattern[str]] = re.compile(
        r"(?<=\b\d)\s+(?=\d\b)|(?<=\d)\s+(?=\.)|(?<=\.)\s+(?=\d)|(?<=\d)\s+(?=%)"
    )

    # Soft-hyphens, zero-width characters, directional overrides
    _HIDDEN_UNICODE_CHARS: Final[re.Pattern[str]] = re.compile(
        r"[\u00AD\u200B\u200C\u200D\u200E\u200F\uFEFF\u2060\u00A0]"
    )

    # Dehyphenate words broken across line wraps and page breaks: e.g., '18-\nmonth' -> '18-month'
    _CROSS_LINE_HYPHEN: Final[re.Pattern[str]] = re.compile(
        r"(\b[a-zA-Z0-9]+)-\s*\n\s*([a-zA-Z0-9]+\b)"
    )

    # Whitespace cleanup patterns
    _HORIZONTAL_WHITESPACE_PATTERN: Final[re.Pattern[str]] = re.compile(r"[ \t]+")
    _CONSECUTIVE_NEWLINES_PATTERN: Final[re.Pattern[str]] = re.compile(r"\n{3,}")

    @classmethod
    def normalize(cls, raw_text: str) -> str:
        """Executes the complete sanitization routine on raw input text.

        Args:
            raw_text: Raw string extracted from document ingestion.

        Returns:
            str: Standardized, de-obfuscated plain text ready for rule evaluation.
        """
        if not raw_text or not raw_text.strip():
            return ""

        # Step 1: Normalize Unicode characters (NFKC) and strip zero-width obfuscations
        normalized = unicodedata.normalize("NFKC", raw_text)
        normalized = cls._HIDDEN_UNICODE_CHARS.sub("", normalized)

        # Step 2: Standardize all newline sequences across operating systems
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # Step 3: Strip trailing and leading whitespace on each line
        normalized = re.sub(r"[ \t]+$", "", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"^[ \t]+", "", normalized, flags=re.MULTILINE)

        # Step 4: Dehyphenate cross-line word breaks: '18-\nmonth' -> '18-month'
        normalized = cls._CROSS_LINE_HYPHEN.sub(r"\1-\2", normalized)

        # Step 5: Collapse single soft line-wraps into a single space while preserving paragraph breaks (\n\n)
        normalized = re.sub(r"(?<!\n)\n(?!\n)", " ", normalized)

        # Step 6: De-obfuscate spaced numeric patterns ('1 0 0 %' -> '100%', '5 0 %' -> '50%')
        normalized = cls._SPACED_NUMBERS_PATTERN.sub("", normalized)

        # Step 7: Protect intentional multi-space inter-word boundaries before collapsing single letters
        normalized = re.sub(r"[ \t]{2,}", " <WSEP> ", normalized)

        # Step 8: Iteratively collapse single-space character obfuscation ('g u a r a n t e e d' -> 'guaranteed')
        while cls._SPACED_LETTERS_PATTERN.search(normalized):
            normalized = cls._SPACED_LETTERS_PATTERN.sub("", normalized)

        # Step 9: Restore protected word boundaries
        normalized = normalized.replace(" <WSEP> ", " ")

        # Step 10: Replace typographic quotes and non-standard dashes
        normalized = (
            normalized.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
            .replace("—", "-")
            .replace("–", "-")
        )

        # Step 11: Collapse multiple horizontal spaces and excessive blank lines
        normalized = cls._HORIZONTAL_WHITESPACE_PATTERN.sub(" ", normalized)
        normalized = cls._CONSECUTIVE_NEWLINES_PATTERN.sub("\n\n", normalized)

        return normalized.strip()
