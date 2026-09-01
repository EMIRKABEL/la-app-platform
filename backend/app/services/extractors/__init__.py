"""Curriculum extraction sub-package.

Each extractor implements ``BaseExtractor`` so new file types
(PDF, DOCX, XLSX) can be added without changing the service layer.
"""

from app.services.extractors.base import BaseExtractor, ExtractionResult
from app.services.extractors.pptx_extractor import PptxExtractor

__all__ = [
    "BaseExtractor",
    "ExtractionResult",
    "PptxExtractor",
]
