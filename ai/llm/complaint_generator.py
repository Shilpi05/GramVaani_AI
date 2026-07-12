"""
complaint_generator.py
------------------------
Complaint Generation service for GramVaani AI.

Responsibilities:
    - Load and cache the Gemini client/model
    - Accept a Whisper transcript
    - Return a structured complaint as a Python dict

This module is intentionally framework-agnostic (no Streamlit
imports) so it can be reused outside the UI later - e.g. from
`backend/services` or a future API layer - without modification.

Configuration:
    Requires a `GEMINI_API_KEY` environment variable. Optionally
    override the model via `GEMINI_MODEL` (defaults to
    "gemini-1.5-flash"), and the request timeout via
    `GEMINI_TIMEOUT_SECONDS` (defaults to 45). All are read from a
    `.env` file if present.
"""

import json
import os
import threading
from functools import lru_cache
from typing import Any, Dict

from dotenv import load_dotenv
import google.generativeai as genai

from ai.llm.prompts import build_complaint_prompt

# Load variables from a local .env file (e.g. GEMINI_API_KEY) into
# the process environment, if one exists. Safe no-op if it doesn't.
load_dotenv()

# ----------------------------------------------------------------------
# Model configuration
# ----------------------------------------------------------------------
GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Without an explicit timeout, a network/proxy issue can make the
# Gemini call hang indefinitely with no exception ever raised - which
# leaves the UI stuck on its spinner forever. This bounds the wait so
# a failure surfaces as a catchable, visible error instead.
GEMINI_TIMEOUT_SECONDS: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "45"))

# The exact set of keys every successful response must contain.
REQUIRED_COMPLAINT_KEYS = {
    "complaint_type",
    "department",
    "priority",
    "summary",
    "formal_complaint",
}


class ComplaintGenerationError(Exception):
    """
    Raised whenever complaint generation cannot be completed -
    covers missing API keys, API/network failures, and invalid or
    incomplete JSON returned by Gemini.
    """


@lru_cache(maxsize=1)
def _get_model() -> "genai.GenerativeModel":
    """
    Configures the Gemini client and returns a cached model instance,
    so the API key is validated and the model is constructed only
    once per process.

    Returns:
        A configured Gemini `GenerativeModel` instance.

    Raises:
        ComplaintGenerationError: If `GEMINI_API_KEY` is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ComplaintGenerationError(
            "GEMINI_API_KEY environment variable is not set. "
            "Add it to your .env file to enable complaint generation."
        )

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL_NAME)


def _strip_markdown_fences(raw_text: str) -> str:
    """
    Removes ```json / ``` code fences if Gemini wraps its response in
    one, despite being instructed not to. Defensive cleanup only.

    Args:
        raw_text: The raw text returned by Gemini.

    Returns:
        The text with any surrounding markdown code fences removed.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[len("json"):]
    return cleaned.strip()


def _parse_and_validate(raw_text: str) -> Dict[str, Any]:
    """
    Parses Gemini's raw text response as JSON and validates that it
    contains exactly the fields the app expects.

    Args:
        raw_text: The raw text returned by Gemini.

    Returns:
        A dict guaranteed to contain all of REQUIRED_COMPLAINT_KEYS.

    Raises:
        ComplaintGenerationError: If the text is not valid JSON, is
            not a JSON object, or is missing required keys.
    """
    cleaned_text = _strip_markdown_fences(raw_text)

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ComplaintGenerationError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ComplaintGenerationError(
            "Gemini response was not a JSON object."
        )

    missing_keys = REQUIRED_COMPLAINT_KEYS - parsed.keys()
    if missing_keys:
        raise ComplaintGenerationError(
            f"Gemini response is missing required field(s): "
            f"{', '.join(sorted(missing_keys))}"
        )

    return parsed


def generate_complaint(transcript: str) -> Dict[str, str]:
    """
    Generates a structured, professional complaint from a Whisper
    transcript using Gemini.

    Args:
        transcript: Plain text transcript of the citizen's spoken
            complaint (output of `ai/speech/speech_service.py`).

    Returns:
        A dict with exactly these keys: "complaint_type",
        "department", "priority", "summary", "formal_complaint".

    Raises:
        ValueError: If the transcript is empty or blank.
        ComplaintGenerationError: If the Gemini API call fails, or
            the response is empty, invalid, or incomplete JSON.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty. Cannot generate a complaint.")

    prompt = build_complaint_prompt(transcript.strip())

    try:
        model = _get_model()

        # NOTE: passing request_options={"timeout": ...} directly to
        # the Gemini SDK is NOT reliable - both the deprecated
        # google-generativeai client and the newer google-genai
        # client have known issues where requests can still hang
        # indefinitely regardless of the timeout supplied to them
        # (this is a documented SDK-level bug, not a config mistake).
        #
        # To guarantee this app never hangs forever regardless of
        # what the SDK/network does internally, the call is run in a
        # daemon background thread and we enforce our OWN hard
        # timeout by joining with a deadline. If it doesn't finish in
        # time, we give up and raise a clear error. Being a daemon
        # thread, an abandoned call can never block the app (or the
        # Python process) from continuing/exiting.
        call_result: Dict[str, Any] = {}

        def _run_gemini_call() -> None:
            try:
                call_result["response"] = model.generate_content(prompt)
            except Exception as thread_exc:  # noqa: BLE001
                call_result["error"] = thread_exc

        worker = threading.Thread(target=_run_gemini_call, daemon=True)
        worker.start()
        worker.join(timeout=GEMINI_TIMEOUT_SECONDS)

        if worker.is_alive():
            raise ComplaintGenerationError(
                f"Gemini did not respond within {GEMINI_TIMEOUT_SECONDS} "
                "seconds. This usually means a network, firewall, or "
                "proxy issue is blocking access to Gemini's API - check "
                "your internet connection and try again."
            )

        if "error" in call_result:
            raise call_result["error"]

        response = call_result["response"]
        raw_text = response.text
    except ComplaintGenerationError:
        # Re-raise configuration errors and timeouts as-is.
        raise
    except Exception as exc:
        # Wrap any other Gemini SDK / network-level failure in a
        # clean, catchable error so the calling UI layer can display
        # a friendly message instead of a raw stack trace.
        raise ComplaintGenerationError(f"Gemini API call failed: {exc}") from exc

    if not raw_text or not raw_text.strip():
        raise ComplaintGenerationError("Gemini returned an empty response.")

    return _parse_and_validate(raw_text)
