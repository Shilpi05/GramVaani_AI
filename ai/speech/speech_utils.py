"""
speech_utils.py
-----------------
Utility functions supporting the Speech-to-Text module.

Responsibilities:
    - Validate uploaded audio file extensions
    - Save uploaded audio to a temporary location on disk
    - Generate collision-free temporary filenames
    - Delete temporary audio files after processing

This module contains NO Whisper/model logic - see `speech_service.py`
for the actual transcription logic. Keeping file I/O separate from
model logic makes both pieces easier to test and reuse independently.
"""

from pathlib import Path
from typing import Optional, Set
import uuid

# ----------------------------------------------------------------------
# Supported audio formats for Speech-to-Text (per task scope)
# ----------------------------------------------------------------------
ALLOWED_EXTENSIONS: Set[str] = {"wav", "mp3", "m4a"}

# Temporary audio files are stored here before/after transcription.
TEMP_AUDIO_DIR: Path = Path("uploads") / "temp_audio"


def is_supported_extension(filename: str) -> bool:
    """
    Checks whether a filename has a supported audio extension.

    Args:
        filename: Original filename of the uploaded audio file.

    Returns:
        True if the extension is one of ALLOWED_EXTENSIONS, else False.
    """
    if "." not in filename:
        return False
    extension = filename.rsplit(".", maxsplit=1)[-1].lower()
    return extension in ALLOWED_EXTENSIONS


def generate_temp_filename(original_filename: str) -> str:
    """
    Generates a collision-free temporary filename for an uploaded
    audio file, preserving its original extension.

    Args:
        original_filename: The filename as uploaded by the user.

    Returns:
        A unique filename string, e.g. "a1b2c3d4e5f6.wav".
    """
    extension = original_filename.rsplit(".", maxsplit=1)[-1].lower()
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{extension}"


def save_uploaded_audio(uploaded_file) -> Path:
    """
    Saves an uploaded Streamlit audio file to a temporary location
    on disk so it can be passed to the Whisper model by file path.

    Args:
        uploaded_file: A Streamlit `UploadedFile` object, as returned
            by `st.file_uploader`.

    Returns:
        The path to the saved temporary audio file.

    Raises:
        ValueError: If the uploaded file has an unsupported extension
            or contains no data (empty file).
    """
    if not is_supported_extension(uploaded_file.name):
        raise ValueError(
            f"Unsupported file type: '{uploaded_file.name}'. "
            f"Supported formats are: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )

    audio_bytes = uploaded_file.getvalue()
    if not audio_bytes:
        raise ValueError("The uploaded audio file is empty.")

    # Ensure the temp directory exists before writing to it.
    TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    temp_filename = generate_temp_filename(uploaded_file.name)
    temp_path = TEMP_AUDIO_DIR / temp_filename

    with open(temp_path, "wb") as temp_file:
        temp_file.write(audio_bytes)

    return temp_path


def delete_temp_file(file_path: Optional[Path]) -> None:
    """
    Deletes a temporary audio file if it exists.

    Called after transcription (success or failure) so uploaded
    audio does not accumulate on disk over time.

    Args:
        file_path: Path to the temporary file to remove. Safe to
            call with None - this is a no-op in that case.
    """
    if file_path is None:
        return
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
    except OSError:
        # Deletion failures should never crash the app - worst case
        # the file is cleaned up later by manual/OS temp cleanup.
        pass
