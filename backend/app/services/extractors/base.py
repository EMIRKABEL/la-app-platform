"""Base extractor protocol for curriculum file types.

Each extractor takes raw file bytes and returns a structured
``ExtractionResult`` dict.  New extractors (PDF, DOCX, XLSX)
should subclass ``BaseExtractor`` and implement ``extract``.
"""

from __future__ import annotations

import abc
from typing import Any


class ExtractionResult(dict):
    """Structured extraction result.

    Top-level shape::

        {
            "source_type": "pptx",
            "metadata": { ... },
            "slides": [ ... ],
        }
    """

    pass


class BaseExtractor(abc.ABC):
    """Abstract base for all curriculum extractors."""

    #: The file extension this extractor handles (e.g. ``".pptx"``).
    supported_extension: str = ""

    @abc.abstractmethod
    def extract(self, data: bytes) -> ExtractionResult:
        """Extract structured content from ``data``.

        Args:
            data: Raw file bytes.

        Returns:
            Structured extraction result.
        """
        ...
