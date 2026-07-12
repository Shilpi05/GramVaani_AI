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

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv
import whisper

# Load variables from a local .env file (e.g. WHISPER_MODEL) into
# the process environment, if one exists. Safe no-op if it doesn't.
load_dotenv()

# ----------------------------------------------------------------------
# Model configuration
# ----------------------------------------------------------------------
# The Whisper model size is configurable via the WHISPER_MODEL
# environment variable (see .env), so it can be tuned per-environment
# without touching code. Defaults to "small" when unset - a better
# balance of Hindi transcription accuracy than "base", while still
# being reasonably fast on CPU.
#
# Example .env entry:
#     WHISPER_MODEL=small
#
# Other valid values: "tiny", "base", "small", "medium", "large".
WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL", "small")


@lru_cache(maxsize=1)
def _load_model(model_size: str = WHISPER_MODEL_SIZE) -> "whisper.Whisper":
    """
    Loads the Whisper model, caching it in memory so repeated
    transcription calls do not reload the model from disk each time.

    Args:
        model_size: Whisper model variant to load
            (e.g. "tiny", "base", "small", "medium", "large").
            Defaults to the WHISPER_MODEL_SIZE resolved from the
            WHISPER_MODEL environment variable.

    Returns:
        A loaded Whisper model instance.

    Raises:
        RuntimeError: If the model fails to load (e.g. invalid model
            name, corrupted download, insufficient disk/memory).
    """
    try:
        return whisper.load_model(model_size)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load Whisper model '{model_size}': {exc}"
        ) from exc


def transcribe_audio(audio_path: Union[str, Path], language: Optional[str] = None) -> str:
    """
    Transcribes an audio file into text using Whisper.

    Args:
        audio_path: Path to a local audio file (.wav, .mp3, .m4a).
        language: Optional Whisper language code to force
            transcription in a specific language (e.g. "hi" for
            Hindi, "en" for English). If None, Whisper auto-detects
            the spoken language instead. Passing the correct
            language explicitly is faster and more accurate than
            auto-detection.

    Returns:
        The recognized speech as plain text. Returns an empty
        string if Whisper detects no speech in the audio.

    Raises:
        FileNotFoundError: If the audio file does not exist on disk.
        RuntimeError: If the model fails to load, or if transcription
            fails for any other reason (corrupt audio, unsupported
            codec, model error, etc.).
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        model = _load_model()
        # fp16=False: forces stable FP32 decoding (this app runs on
        #   CPU, where FP16 is unsupported and silently falls back
        #   anyway - being explicit avoids inconsistent precision).
        # temperature=0.0: deterministic decoding: reduces the model
        #   inventing plausible-sounding but wrong words on quiet,
        #   short, or noisy audio ("hallucination").
        # condition_on_previous_text=False: stops one hallucinated
        #   segment from biasing/compounding into the next one.
        result = model.transcribe(
            str(audio_path),
            language=language,
            fp16=False,
            temperature=0.0,
            condition_on_previous_text=False,
        )
    except RuntimeError:
        # Raised by _load_model() for a model-loading failure -
        # re-raise as-is so the message stays specific to loading.
        raise
    except Exception as exc:
        # Wrap any Whisper/ffmpeg-level failure in a clean, catchable
        # error so the calling UI layer can display a friendly message.
        raise RuntimeError(f"Speech transcription failed: {exc}") from exc

    transcript = result.get("text", "").strip()
    return transcript
