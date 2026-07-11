"""
speech_service.py
--------------------
Core Speech-to-Text service for GramVaani AI.

Responsibilities:
    - Load and cache the Whisper model
    - Accept an audio file path
    - Return the transcribed text

This module is intentionally framework-agnostic (no Streamlit
imports) so it can be reused outside the UI later - e.g. from
`backend/services` or a future API layer - without modification.
"""

from functools import lru_cache
from pathlib import Path
from typing import Union

import whisper

# ----------------------------------------------------------------------
# Model configuration
# ----------------------------------------------------------------------
# "base" balances speed and accuracy for a first integration.
# Larger variants ("small", "medium", "large") are more accurate but
# slower and heavier - revisit once real usage patterns are known.
WHISPER_MODEL_SIZE: str = "base"


@lru_cache(maxsize=1)
def _load_model(model_size: str = WHISPER_MODEL_SIZE) -> "whisper.Whisper":
    """
    Loads the Whisper model, caching it in memory so repeated
    transcription calls do not reload the model from disk each time.

    Args:
        model_size: Whisper model variant to load
            (e.g. "tiny", "base", "small", "medium", "large").

    Returns:
        A loaded Whisper model instance.
    """
    return whisper.load_model(model_size)


def transcribe_audio(audio_path: Union[str, Path]) -> str:
    """
    Transcribes an audio file into text using Whisper.

    Args:
        audio_path: Path to a local audio file (.wav, .mp3, .m4a).

    Returns:
        The recognized speech as plain text. Returns an empty
        string if Whisper detects no speech in the audio.

    Raises:
        FileNotFoundError: If the audio file does not exist on disk.
        RuntimeError: If transcription fails for any other reason
            (corrupt audio, unsupported codec, model error, etc.).
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        model = _load_model()
        result = model.transcribe(str(audio_path))
    except Exception as exc:
        # Wrap any Whisper/ffmpeg-level failure in a clean, catchable
        # error so the calling UI layer can display a friendly message.
        raise RuntimeError(f"Speech transcription failed: {exc}") from exc

    transcript = result.get("text", "").strip()
    return transcript
