"""
speech_service.py
--------------------
Core Speech-to-Text service for GramVaani AI - built on Groq's hosted
Whisper API (`client.audio.transcriptions.create`), reached through
the exact same `groq` Python SDK and `GROQ_API_KEY` already used by
`ai/llm/complaint_generator.py`.

Self-hosted `openai-whisper` has been completely removed from this
module. Running Whisper locally pulled in the full `torch` + CUDA
dependency stack (useless on a CPU-only host like Streamlit Community
Cloud) and required downloading a 461MB-1.4GB model file on every
cold start, which was exceeding that platform's free-tier memory
limit and causing deploy crashes. Groq hosts Whisper itself, so this
module now sends the audio file to Groq's API instead of loading any
model into this process at all - there is no model download, and no
model-sized memory footprint here anymore.

Responsibilities:
    - Load the Groq API key from .env (shared with
      ai/llm/complaint_generator.py)
    - Send an audio file to Groq's hosted Whisper endpoint
    - Return the transcribed text

Public API (unchanged from the previous local-Whisper implementation,
so no frontend code needs to change):
    transcribe_audio(audio_path, language=None) -> str

This module is intentionally framework-agnostic (no Streamlit
imports) so it can be reused outside the UI later - e.g. from
`backend/services` or a future API layer - without modification.

Configuration (all read from .env via python-dotenv):
    GROQ_API_KEY            - required. No default; raises a clean
                               RuntimeError if missing. The same key
                               ai/llm/complaint_generator.py uses.
    GROQ_WHISPER_MODEL       - optional. Defaults to
                               "whisper-large-v3-turbo" if unset or
                               blank (Groq's recommended choice for
                               multilingual price/performance - see
                               https://console.groq.com/docs/speech-to-text).
                               Use "whisper-large-v3" instead for
                               maximum accuracy over speed.
    GROQ_TIMEOUT_SECONDS     - optional, defaults to 30. Shared with
                               ai/llm/complaint_generator.py - one
                               .env value controls both.
    GROQ_RETRY_ATTEMPTS      - optional, defaults to 3. Shared with
                               ai/llm/complaint_generator.py.

Note: Groq's free tier caps audio file size at 25MB per request (100MB
on paid tiers) - see https://console.groq.com/docs/speech-to-text.
"""

import logging
import os
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union

from dotenv import load_dotenv
from groq import Groq

# Load variables from a local .env file (e.g. GROQ_API_KEY) into the
# process environment, if one exists. Safe no-op if it doesn't -
# ai/llm/complaint_generator.py also calls this; python-dotenv's
# load_dotenv() is idempotent, so calling it from both modules is
# harmless regardless of import order.
load_dotenv()

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
logger = logging.getLogger("gramvaani.ai.speech.speech_service")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


def _env_or_default(name: str, default: str) -> str:
    """
    Reads an environment variable, falling back to `default` if the
    variable is either completely unset OR present but blank/
    whitespace-only (e.g. `GROQ_WHISPER_MODEL=` with nothing after
    the `=` in `.env`).

    Plain `os.getenv(name, default)` does NOT handle the blank case -
    if the variable exists with an empty value, it returns "" instead
    of `default`. Mirrors the identical helper in
    `ai/llm/complaint_generator.py` (duplicated here rather than
    shared, since each ai/ submodule is kept standalone/importable on
    its own).

    Args:
        name: Environment variable name to read.
        default: Value to use if the variable is unset or blank.

    Returns:
        The trimmed environment value, or `default`.
    """
    value = os.getenv(name, "").strip()
    return value if value else default


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
GROQ_TIMEOUT_SECONDS: int = int(_env_or_default("GROQ_TIMEOUT_SECONDS", "30"))
GROQ_RETRY_ATTEMPTS: int = int(_env_or_default("GROQ_RETRY_ATTEMPTS", "3"))
GROQ_WHISPER_MODEL: str = _env_or_default(
    "GROQ_WHISPER_MODEL", "whisper-large-v3-turbo"
)


@lru_cache(maxsize=1)
def _get_client() -> "Groq":
    """
    Builds and caches a single Groq client for the lifetime of the
    process - the exact same construction pattern
    `ai/llm/complaint_generator.py` uses for its own client.

    Returns:
        A configured `Groq` client instance.

    Raises:
        RuntimeError: If `GROQ_API_KEY` is not set.
    """
    api_key = _env_or_default("GROQ_API_KEY", "")
    if not api_key:
        logger.error("GROQ_API_KEY is not set - cannot create Groq client.")
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Add it to your .env file to enable speech-to-text."
        )

    return Groq(
        api_key=api_key,
        timeout=GROQ_TIMEOUT_SECONDS,
        max_retries=GROQ_RETRY_ATTEMPTS,
    )


def transcribe_audio(audio_path: Union[str, Path], language: Optional[str] = None) -> str:
    """
    Transcribes an audio file into text using Groq's hosted Whisper
    API.

    Args:
        audio_path: Path to a local audio file (.wav, .mp3, .m4a).
        language: Optional ISO-639-1 language code to force
            transcription in a specific language (e.g. "hi" for
            Hindi, "en" for English). If None, Whisper auto-detects
            the spoken language instead. Passing the correct
            language explicitly is faster and more accurate than
            auto-detection - identical behavior to the previous
            local-Whisper implementation.

    Returns:
        The recognized speech as plain text. Returns an empty string
        if Whisper detects no speech in the audio.

    Raises:
        FileNotFoundError: If the audio file does not exist on disk.
        RuntimeError: If the API key is missing, the request times
            out, or transcription fails for any other reason (corrupt
            audio, unsupported codec, network/API error, etc.). This
            matches the previous local-Whisper implementation's error
            contract exactly, so callers do not need to change.
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    client = _get_client()

    # NOTE: passing timeout=/max_retries= to the Groq client above is
    # the documented way to get bounded retries and a timeout - but
    # ai/llm/complaint_generator.py's own history on this exact
    # project found that relying solely on an SDK's own timeout can
    # still hang past it in practice. The same daemon-thread hard
    # timeout used there is used here for the same reason: it
    # guarantees this call returns control within GROQ_TIMEOUT_SECONDS
    # no matter what the SDK/network does internally.
    call_result: Dict[str, Any] = {}

    def _run_transcription_call() -> None:
        try:
            with open(audio_path, "rb") as audio_file:
                call_result["response"] = client.audio.transcriptions.create(
                    file=audio_file,
                    model=GROQ_WHISPER_MODEL,
                    language=language,
                    response_format="text",
                    temperature=0.0,
                )
        except Exception as thread_exc:  # noqa: BLE001
            call_result["error"] = thread_exc

    worker = threading.Thread(target=_run_transcription_call, daemon=True)
    worker.start()
    worker.join(timeout=GROQ_TIMEOUT_SECONDS)

    if worker.is_alive():
        logger.error(
            "Groq transcription using model '%s' did not respond within "
            "%d second(s).",
            GROQ_WHISPER_MODEL,
            GROQ_TIMEOUT_SECONDS,
        )
        raise RuntimeError(
            f"Speech transcription did not respond within "
            f"{GROQ_TIMEOUT_SECONDS} seconds. This usually means a "
            "network, firewall, or proxy issue is blocking access to "
            "Groq's API - check your internet connection and try again."
        )

    if "error" in call_result:
        exc = call_result["error"]
        logger.error(
            "Groq transcription failed using model '%s': %s",
            GROQ_WHISPER_MODEL,
            exc,
        )
        raise RuntimeError(f"Speech transcription failed: {exc}") from exc

    response = call_result.get("response")
    # response_format="text" returns a plain string on current SDK
    # versions; fall back to a `.text` attribute defensively in case
    # a future SDK version wraps it in an object instead.
    transcript = response if isinstance(response, str) else getattr(response, "text", "")

    return transcript.strip()