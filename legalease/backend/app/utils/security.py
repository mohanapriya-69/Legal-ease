"""Security helpers: logo validation and safe filename derivation."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from app.config import settings
from app.utils.errors import UploadError

# Magic-byte signatures. Extensions and client-supplied content types are
# attacker controlled, so the actual bytes are what we trust.
_MAGIC_BYTES: dict[str, tuple[bytes, ...]] = {
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
}

_EXTENSIONS: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
}

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9 _-]+")
_COLLAPSE_SPACES = re.compile(r"[-_ ]{2,}")


def sniff_image_type(data: bytes) -> str | None:
    """Return the detected MIME type of ``data``, or ``None`` if unrecognised."""
    for mime, signatures in _MAGIC_BYTES.items():
        if any(data.startswith(signature) for signature in signatures):
            return mime
    return None


def validate_logo_upload(data: bytes, declared_content_type: str | None) -> str:
    """Validate logo bytes and return the trusted MIME type.

    Raises :class:`UploadError` for empty, oversized, non-image or
    extension/content-type mismatched payloads.
    """
    if not data:
        raise UploadError("The uploaded file is empty.")

    if len(data) > settings.max_logo_bytes:
        limit_mb = settings.max_logo_bytes / (1024 * 1024)
        raise UploadError(f"The logo must be smaller than {limit_mb:.0f} MB.")

    detected = sniff_image_type(data)
    if detected is None:
        raise UploadError(
            "The logo must be a PNG or JPEG image. Other file types are not accepted."
        )

    if (
        declared_content_type
        and declared_content_type.split(";")[0].strip().lower() in settings.allowed_logo_content_types
        and declared_content_type.split(";")[0].strip().lower() != detected
    ):
        raise UploadError("The logo file does not match its declared file type.")

    return detected


def extension_for(mime: str) -> str:
    return _EXTENSIONS.get(mime, ".png")


def build_logo_filename(stored_name: str | None) -> str:
    """Resolve a stored logo name to a path inside the logo directory.

    The value always originates from the database, but it is re-validated so a
    tampered row cannot escape the upload directory.
    """
    if not stored_name:
        raise UploadError("No logo is associated with this profile.")

    candidate = Path(stored_name).name
    if not candidate or candidate in {".", ".."}:
        raise UploadError("The logo reference is invalid.")

    resolved = (settings.logo_dir / candidate).resolve()
    logo_root = settings.logo_dir.resolve()
    if not resolved.is_relative_to(logo_root):
        raise UploadError("The logo reference is invalid.")

    if not resolved.is_file():
        raise UploadError("The logo file could not be found.")

    return str(resolved)


def safe_download_filename(title: str, extension: str) -> str:
    """Derive an ASCII attachment filename from a user-supplied title.

    Strips directory separators, traversal sequences, control characters and
    non-ASCII glyphs so the value is safe in a ``Content-Disposition`` header.
    """
    normalized = unicodedata.normalize("NFKD", title or "document")
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = _UNSAFE_FILENAME_CHARS.sub(" ", ascii_only)
    cleaned = _COLLAPSE_SPACES.sub(" ", cleaned).strip(" ._-")

    if not cleaned:
        cleaned = "document"

    # Keep well under the ~255 byte filename limit on every platform.
    cleaned = cleaned[:80].strip(" ._-") or "document"

    suffix = extension if extension.startswith(".") else f".{extension}"
    return f"{cleaned}{suffix}"
