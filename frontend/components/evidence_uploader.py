"""
evidence_uploader.py
----------------------
Reusable "Upload Evidence" component for GramVaani AI.

Lets a citizen optionally attach a photo (jpg/jpeg/png) as supporting
evidence alongside their voice complaint. This is intentionally
lightweight: no image AI, no classification - the image is saved to
disk, previewed, and its metadata is recorded in `st.session_state` so
other parts of the app (the generated complaint card) can note that
evidence was attached, without ever inspecting the image's contents.

This module owns:
    - Validating and saving the uploaded image to `uploads/images/`
    - Deleting a replaced/cleared image from disk
    - Rendering the upload widget, preview, filename/size, and the
      empty-state placeholder shown before anything is uploaded

Session state:
    `EVIDENCE_STATE_KEY` holds either None (nothing uploaded) or a
    dict: {"path": str, "filename": str, "size_bytes": int}. Public
    (no leading underscore) because `frontend/pages/file_complaint.py`
    reads it to show an "evidence attached" note once a complaint is
    generated.
"""

import uuid
from pathlib import Path
from typing import Optional, Set

import streamlit as st

from frontend.components.theme import placeholder_card
from frontend.config.constants import (
    EVIDENCE_EMPTY_STATE_TEXT,
    EVIDENCE_FILE_TOO_LARGE_ERROR,
    EVIDENCE_INVALID_TYPE_ERROR,
    EVIDENCE_REMOVE_BUTTON_LABEL,
    EVIDENCE_UPLOAD_SUCCESS_MESSAGE,
    EVIDENCE_UPLOADER_HELP,
    EVIDENCE_UPLOADER_LABEL,
)

# ----------------------------------------------------------------------
# File handling configuration
# ----------------------------------------------------------------------
ALLOWED_EXTENSIONS: Set[str] = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB - generous for a phone photo

# Where evidence images are saved. Relative to the app's working
# directory, mirroring `ai/speech/speech_utils.py`'s TEMP_AUDIO_DIR.
EVIDENCE_DIR: Path = Path("uploads") / "images"

# Public (no leading underscore) - read by
# `frontend/pages/file_complaint.py` to know whether to show an
# "evidence attached" note on the generated complaint card.
EVIDENCE_STATE_KEY: str = "gv_evidence_image"


def is_supported_image_extension(filename: str) -> bool:
    """
    Checks whether a filename has a supported image extension.

    Args:
        filename: Original filename of the uploaded image.

    Returns:
        True if the extension is one of ALLOWED_EXTENSIONS, else False.
    """
    if "." not in filename:
        return False
    extension = filename.rsplit(".", maxsplit=1)[-1].lower()
    return extension in ALLOWED_EXTENSIONS


def format_file_size(num_bytes: int) -> str:
    """
    Formats a byte count as a short, human-readable string.

    Args:
        num_bytes: File size in bytes.

    Returns:
        A string like "482 KB" or "1.3 MB".
    """
    size = float(num_bytes)
    for unit in ("bytes", "KB", "MB"):
        if size < 1024 or unit == "MB":
            return f"{size:.0f} {unit}" if unit == "bytes" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} bytes"  # pragma: no cover - unreachable, defensive only


def save_evidence_image(uploaded_file) -> Path:
    """
    Saves an uploaded Streamlit image file to `uploads/images/` with a
    collision-free filename, preserving the original extension.

    Args:
        uploaded_file: A Streamlit `UploadedFile` object, as returned
            by `st.file_uploader`.

    Returns:
        The path to the saved image file.

    Raises:
        ValueError: If the file has an unsupported extension, is
            empty, or exceeds MAX_FILE_SIZE_BYTES.
    """
    if not is_supported_image_extension(uploaded_file.name):
        raise ValueError(EVIDENCE_INVALID_TYPE_ERROR)

    image_bytes = uploaded_file.getvalue()
    if not image_bytes:
        raise ValueError(EVIDENCE_INVALID_TYPE_ERROR)
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(EVIDENCE_FILE_TOO_LARGE_ERROR)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    extension = uploaded_file.name.rsplit(".", maxsplit=1)[-1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    saved_path = EVIDENCE_DIR / unique_filename

    with open(saved_path, "wb") as saved_file:
        saved_file.write(image_bytes)

    return saved_path


def delete_evidence_image(file_path: Optional[str]) -> None:
    """
    Deletes a saved evidence image from disk, if it exists.

    Safe to call with None or a path that no longer exists - both are
    no-ops. Never raises, since a cleanup failure should never crash
    the page.

    Args:
        file_path: String path to the file to remove.
    """
    if not file_path:
        return
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
    except OSError:
        pass


def _get_evidence_state() -> Optional[dict]:
    """Returns the current evidence metadata dict, or None."""
    return st.session_state.get(EVIDENCE_STATE_KEY)


def _handle_new_upload(uploaded_file) -> None:
    """
    Saves a newly uploaded evidence image and updates session state.
    Replaces (and, if the "auto delete files" preference is on,
    deletes from disk) any previously attached evidence image first.

    Args:
        uploaded_file: The Streamlit `UploadedFile` from the widget.
    """
    previous = _get_evidence_state()

    try:
        saved_path = save_evidence_image(uploaded_file)
    except ValueError as exc:
        st.error(str(exc))
        return

    # Clean up the previous file before recording the new one, so a
    # citizen replacing their photo doesn't silently accumulate old
    # images on disk - gated by the "Auto delete uploaded files"
    # preference set on the Settings page (default: on).
    if previous and st.session_state.get("gv_auto_delete_files", True):
        delete_evidence_image(previous.get("path"))

    st.session_state[EVIDENCE_STATE_KEY] = {
        "path": str(saved_path),
        "filename": uploaded_file.name,
        "size_bytes": len(uploaded_file.getvalue()),
    }
    st.success(EVIDENCE_UPLOAD_SUCCESS_MESSAGE)


def render_evidence_upload_section() -> None:
    """
    Renders the full "Upload Evidence" experience: the file uploader,
    an image preview with filename/size once something is attached, a
    "Remove" button, and an informative placeholder when nothing has
    been uploaded yet this session.
    """
    uploaded_file = st.file_uploader(
        label=EVIDENCE_UPLOADER_LABEL,
        type=sorted(ALLOWED_EXTENSIONS),
        help=EVIDENCE_UPLOADER_HELP,
        key="gv_evidence_uploader",
    )

    if uploaded_file is not None:
        current = _get_evidence_state()
        # Only treat this as a *new* upload if the filename changed -
        # Streamlit reruns the whole script on every interaction, so
        # without this check we'd re-save the same file on every
        # unrelated click elsewhere on the page.
        if current is None or current.get("filename") != uploaded_file.name:
            _handle_new_upload(uploaded_file)

    evidence = _get_evidence_state()

    if evidence is None:
        placeholder_card(
            icon="🖼",
            text=EVIDENCE_EMPTY_STATE_TEXT,
        )
        return

    saved_path = Path(evidence["path"])
    if saved_path.exists():
        st.image(str(saved_path), use_container_width=True)

    st.caption(f"📎 {evidence['filename']} · {format_file_size(evidence['size_bytes'])}")

    if st.button(
        EVIDENCE_REMOVE_BUTTON_LABEL,
        use_container_width=True,
        key="gv_remove_evidence_button",
    ):
        delete_evidence_image(evidence.get("path"))
        st.session_state[EVIDENCE_STATE_KEY] = None
        st.session_state.pop("gv_evidence_uploader", None)
        st.rerun()
