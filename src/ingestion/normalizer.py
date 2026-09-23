"""Text sanitization and anti-obfuscation pipeline component for FinGuard-AI.

Removes deliberate spacing tricks, leetspeak anomalies, and irregular line breaks
often inserted into predatory agreements to evade automated detection systems.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Final


class TextNormalizer:
    """Sanitizes, unescapes, and de-obfuscates text extracted from investment agreements."""

    # Matches single-character spacing within a word: e.g., 'g u a r a n t e e d' -> 'guaranteed'
    _SPACED_LETTERS_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?<=\b[a-zA-Z]) (?=[a-zA-Z]\b)")

    # Matches spaced percentage/number patterns: e.g., '1 0 0 %' -> '100%', '1 . 5 %' -> '1.5%'
    _SPACED_NUMBERS_PATTERN: Final[re.Pattern[str]] = re.compile(
        r"(?<=\b\d)\s+(?=\d\b)|(?<=\d)\s+(?=\.)|(?<=\.)\s+(?=\d)|(?<=\d)\s+(?=%)"
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

        # Step 1: Normalize Unicode characters (NFKC)
        normalized = unicodedata.normalize("NFKC", raw_text)

        # Step 2: Standardize all newline sequences across operating systems
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # Step 3: De-obfuscate spaced numeric patterns ('1 0 0 %' -> '100%', '5 0 %' -> '50%')
        normalized = cls._SPACED_NUMBERS_PATTERN.sub("", normalized)

        # Step 4: Protect intentional multi-space inter-word boundaries before collapsing single letters
        normalized = re.sub(r"[ \t]{2,}", " <WSEP> ", normalized)

        # Step 5: Iteratively collapse single-space character obfuscation ('g u a r a n t e e d' -> 'guaranteed')
        while cls._SPACED_LETTERS_PATTERN.search(normalized):
            normalized = cls._SPACED_LETTERS_PATTERN.sub("", normalized)

        # Step 6: Restore protected word boundaries
        normalized = normalized.replace(" <WSEP> ", " ")

        # Step 7: Replace typographic quotes and non-standard dashes
        normalized = (
            normalized.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
            .replace("—", "-")
            .replace("–", "-")
        )

        # Step 8: Collapse multiple horizontal spaces and excessive blank lines
        normalized = cls._HORIZONTAL_WHITESPACE_PATTERN.sub(" ", normalized)
        normalized = cls._CONSECUTIVE_NEWLINES_PATTERN.sub("\n\n", normalized)

        return normalized.strip()
