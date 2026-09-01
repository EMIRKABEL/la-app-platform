"""Storage provider abstraction layer.

The ``StorageProvider`` protocol defines a minimal interface for saving
and retrieving files.  ``LocalStorageProvider`` is the default
implementation for development.  Future implementations (S3, R2, MinIO)
can be added without changing lesson or curriculum logic.
"""

from __future__ import annotations

import abc
import os
import re
import uuid
from pathlib import Path


# ── Security helpers ──────────────────────────────────────────────

_UNSAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]")


def sanitize_filename(filename: str) -> str:
    """Return a filesystem-safe version of ``filename``.

    Removes path separators, null bytes, and other characters that
    should never appear in a filename.  Preserves the extension.
    """
    # Strip any directory components the client might have sent
    basename = os.path.basename(filename)
    # Replace whitespace and unsafe characters with underscores
    safe = _UNSAFE_CHARS.sub("_", basename)
    # Collapse multiple underscores
    safe = re.sub(r"_{2,}", "_", safe)
    # Strip leading dots/underscores
    safe = safe.lstrip("._")
    # Fallback
    if not safe:
        safe = f"upload_{uuid.uuid4().hex[:8]}"
    return safe


# ── Protocol / ABC ────────────────────────────────────────────────


class StorageProvider(abc.ABC):
    """Abstract storage provider.

    Implementations must provide ``save_file`` and ``file_exists``.
    """

    @abc.abstractmethod
    def save_file(
        self,
        *,
        course_id: str,
        unit_id: str,
        lesson_id: str,
        original_filename: str,
        data: bytes,
    ) -> str:
        """Save ``data`` and return the relative storage path.

        The path returned should be relative to the storage root and
        must not contain absolute system paths.
        """
        ...

    @abc.abstractmethod
    def file_exists(self, storage_path: str) -> bool:
        """Return ``True`` if a file exists at ``storage_path``."""
        ...

    @abc.abstractmethod
    def read_file(self, storage_path: str) -> bytes:
        """Return the raw bytes of the file at ``storage_path``."""
        ...


class LocalStorageProvider(StorageProvider):
    """Store files on the local filesystem during development.

    Files are stored under::

        {storage_root}/curriculum/{course_id}/{unit_id}/{lesson_id}/{safe_filename}

    To switch to S3, R2, or MinIO later, create a new class that
    implements ``StorageProvider`` and inject it where
    ``LocalStorageProvider`` is currently used — no lesson logic
    needs to change.
    """

    def __init__(self, storage_root: str) -> None:
        self._root = Path(storage_root).resolve()

    def save_file(
        self,
        *,
        course_id: str,
        unit_id: str,
        lesson_id: str,
        original_filename: str,
        data: bytes,
    ) -> str:
        safe_name = sanitize_filename(original_filename)
        rel_dir = Path("curriculum") / course_id / unit_id / lesson_id
        abs_dir = self._root / rel_dir
        abs_dir.mkdir(parents=True, exist_ok=True)

        # If the file already exists, prepend a short UUID to avoid
        # silent overwrite.
        target = abs_dir / safe_name
        if target.exists():
            stem = target.stem
            suffix = target.suffix
            safe_name = f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"
            target = abs_dir / safe_name

        target.write_bytes(data)

        # Return a forward-slash path relative to the storage root
        return str(rel_dir / safe_name).replace("\\", "/")

    def file_exists(self, storage_path: str) -> bool:
        return (self._root / storage_path).is_file()

    def read_file(self, storage_path: str) -> bytes:
        """Return the raw bytes of the file at ``storage_path``."""
        return (self._root / storage_path).read_bytes()
