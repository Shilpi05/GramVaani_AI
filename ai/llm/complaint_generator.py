"""
complaint_generator.py
------------------------
Complaint Generation service for GramVaani AI - built entirely on
Groq's official Python SDK (`groq`).

Google Gemini (`google.generativeai` / `google.genai`) has been
completely removed from this module. Gemini's `generate_content()`
call was repeatedly failing on this project due to Google-side
quota/model-availability issues (despite a valid API key and working
model listing), which was blocking the project. This module now talks
to Groq instead.

Responsibilities:
    - Load the Groq API key from .env
    - Call Groq's chat completions endpoint with a primary model,
      automatically falling back to a secondary model if the primary
      model is unavailable or the call otherwise fails
    - Call Groq with retries (exponential backoff) and a hard
      timeout that is guaranteed to fire even if the SDK's own
      timeout mechanism does not
    - Parse and validate the JSON response
    - Strip markdown code fences if the model wraps its JSON in one
    - Return a plain dict - the exact same public shape the frontend
      has always expected

Public API (unchanged from the previous Gemini-based implementation,
so no frontend code needs to change):
    generate_complaint(transcript: str) -> Dict[str, str]
    ComplaintGenerationError (exception class)

This module is intentionally framework-agnostic (no Streamlit
imports) so it can be reused outside the UI later - e.g. from
`backend/services` or a future API layer - without modification.

Configuration (all read from .env via python-dotenv):
    GROQ_API_KEY           - required. No default; raises a clean
                              ComplaintGenerationError if missing.
    GROQ_MODEL              - optional. Defaults to
                              "llama-3.3-70b-versatile" if unset or
                              blank.
    GROQ_FALLBACK_MODEL     - optional. Defaults to
                              "llama-3.1-8b-instant" if unset or
                              blank. Used automatically if the
                              primary model is unavailable or the
                              call to it fails.
    GROQ_TIMEOUT_SECONDS    - optional, defaults to 30.
    GROQ_RETRY_ATTEMPTS     - optional, defaults to 3.
"""

import json
import logging
import os
import threading
from functools import lru_cache
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from groq import Groq

from ai.llm.prompts import build_complaint_prompt

# Load variables from a local .env file (e.g. GROQ_API_KEY) into the
# process environment, if one exists. Safe no-op if it doesn't.
load_dotenv()

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
# A dedicated, namespaced logger so these messages are easy to filter
# in server logs without configuring logging globally for the whole
# app. If the hosting app has already configured logging/handlers,
# this will simply use that configuration instead of adding a
# duplicate handler.
logger = logging.getLogger("gramvaani.ai.llm.complaint_generator")
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
    whitespace-only (e.g. `GROQ_MODEL=` with nothing after the `=`
    in `.env`).

    Plain `os.getenv(name, default)` does NOT handle the blank case -
    if the variable exists with an empty value, it returns "" instead
    of `default`. This is a common and easy-to-miss .env footgun, and
    is handled centrally here for every setting in this module.

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

# Primary and fallback model names. Both are hardcoded defaults per
# project requirements, but may be overridden via .env.
GROQ_PRIMARY_MODEL: str = _env_or_default("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_FALLBACK_MODEL: str = _env_or_default(
    "GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant"
)


class ComplaintGenerationError(Exception):
    """
    Raised whenever complaint generation cannot be completed for any
    reason - covers missing/invalid API keys, API or network
    failures, timeouts, both the primary and fallback model failing,
    and invalid or incomplete JSON returned by the model. Callers
    only ever need to catch this one exception type; a raw Python
    traceback should never surface.
    """


@lru_cache(maxsize=1)
def _get_client() -> "Groq":
    """
    Builds and caches a single Groq client for the lifetime of the
    process, configured with:
        - the API key loaded from .env
        - an SDK-level timeout (GROQ_TIMEOUT_SECONDS)
        - SDK-level retries (GROQ_RETRY_ATTEMPTS)

    Returns:
        A configured `Groq` client instance.

    Raises:
        ComplaintGenerationError: If `GROQ_API_KEY` is not set.
    """
    api_key = _env_or_default("GROQ_API_KEY", "")
    if not api_key:
        logger.error("GROQ_API_KEY is not set - cannot create Groq client.")
        raise ComplaintGenerationError(
            "GROQ_API_KEY environment variable is not set. "
            "Add it to your .env file to enable complaint generation."
        )

    logger.info(
        "Loaded GROQ_API_KEY from environment (length=%d characters).",
        len(api_key),
    )

    return Groq(
        api_key=api_key,
        timeout=GROQ_TIMEOUT_SECONDS,
        max_retries=GROQ_RETRY_ATTEMPTS,
    )


def _strip_markdown_fences(raw_text: str) -> str:
    """
    Removes ```json / ``` code fences if the model wraps its response
    in one, despite being instructed not to. Defensive cleanup only.

    Args:
        raw_text: The raw text returned by the model.

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
    Parses the model's raw text response as JSON and validates that
    it contains exactly the fields the app expects.

    Args:
        raw_text: The raw text returned by the model.

    Returns:
        A dict guaranteed to contain all required complaint fields.

    Raises:
        ComplaintGenerationError: If the text is not valid JSON, is
            not a JSON object, or is missing required keys.
    """
    required_keys = {
        "complaint_type",
        "department",
        "priority",
        "summary",
        "formal_complaint",
    }

    cleaned_text = _strip_markdown_fences(raw_text)

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ComplaintGenerationError(
            f"Groq returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ComplaintGenerationError("Groq response was not a JSON object.")

    missing_keys = required_keys - parsed.keys()
    if missing_keys:
        raise ComplaintGenerationError(
            f"Groq response is missing required field(s): "
            f"{', '.join(sorted(missing_keys))}"
        )

    return parsed


def _call_groq_model(client: "Groq", model_name: str, prompt: str) -> str:
    """
    Calls Groq's chat completions endpoint with a single model, using
    a hard timeout enforced in a background daemon thread.

    NOTE: the SDK's own `timeout=` / `max_retries=` configured on the
    client is the officially documented way to get bounded retries
    and a timeout - but relying solely on an SDK's internal timeout
    handling has, historically (see the previous Gemini
    implementation of this module), proven insufficient to GUARANTEE
    a call never hangs. To guarantee this app never hangs forever no
    matter what the SDK/network does internally, the call is
    additionally run in a daemon background thread with our own hard
    join() deadline. Being a daemon thread, an abandoned call can
    never block the app (or the Python process) from continuing or
    exiting.

    Args:
        client: The configured Groq client.
        model_name: The Groq model to call.
        prompt: The full prompt to send.

    Returns:
        The raw text content of the model's response.

    Raises:
        ComplaintGenerationError: On timeout, API failure, or an
            empty response.
    """
    call_result: Dict[str, Any] = {}

    def _run_groq_call() -> None:
        try:
            call_result["response"] = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
        except Exception as thread_exc:  # noqa: BLE001
            call_result["error"] = thread_exc

    worker = threading.Thread(target=_run_groq_call, daemon=True)
    worker.start()
    worker.join(timeout=GROQ_TIMEOUT_SECONDS)

    if worker.is_alive():
        logger.error(
            "Groq call using model '%s' did not respond within %d "
            "second(s).",
            model_name,
            GROQ_TIMEOUT_SECONDS,
        )
        raise ComplaintGenerationError(
            f"Groq did not respond within {GROQ_TIMEOUT_SECONDS} "
            f"seconds using model '{model_name}'. This usually means a "
            "network, firewall, or proxy issue is blocking access to "
            "Groq's API - check your internet connection and try again."
        )

    if "error" in call_result:
        exc = call_result["error"]
        logger.error(
            "Groq generation failed using model '%s': %s", model_name, exc
        )
        raise ComplaintGenerationError(
            f"Groq API call failed using model '{model_name}': {exc}"
        ) from exc

    response = call_result.get("response")
    raw_text: Optional[str] = None
    try:
        raw_text = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        logger.error(
            "Groq response using model '%s' had an unexpected shape: %s",
            model_name,
            exc,
        )
        raise ComplaintGenerationError(
            f"Groq returned an unexpected response shape using model "
            f"'{model_name}': {exc}"
        ) from exc

    if not raw_text or not raw_text.strip():
        logger.error(
            "Groq returned an empty response using model '%s'.", model_name
        )
        raise ComplaintGenerationError(
            f"Groq returned an empty response using model '{model_name}'."
        )

    return raw_text


def generate_complaint(transcript: str) -> Dict[str, str]:
    """
    Generates a structured, professional complaint from a Whisper
    transcript using Groq.

    Public API - unchanged signature from the previous Gemini-based
    implementation, so no frontend code needs to change.

    Tries `GROQ_PRIMARY_MODEL` ("llama-3.3-70b-versatile" by default)
    first. If that model is unavailable or the call to it fails for
    any reason, this automatically falls back to
    `GROQ_FALLBACK_MODEL` ("llama-3.1-8b-instant" by default) before
    giving up.

    Args:
        transcript: Plain text transcript of the citizen's spoken
            complaint (output of `ai/speech/speech_service.py`).

    Returns:
        A dict with exactly these keys: "complaint_type",
        "department", "priority", "summary", "formal_complaint".

    Raises:
        ValueError: If the transcript is empty or blank.
        ComplaintGenerationError: For any other failure - missing API
            key, API/network failure, timeout on both primary and
            fallback models, or invalid/incomplete JSON. This is the
            only exception type callers need to catch; a raw Python
            traceback should never reach the caller.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty. Cannot generate a complaint.")

    prompt = build_complaint_prompt(transcript.strip())

    try:
        client = _get_client()
    except ComplaintGenerationError:
        raise
    except Exception as exc:
        logger.error("Failed to prepare Groq client: %s", exc)
        raise ComplaintGenerationError(
            f"Failed to prepare Groq client: {exc}"
        ) from exc

    models_to_try = [GROQ_PRIMARY_MODEL]
    if GROQ_FALLBACK_MODEL and GROQ_FALLBACK_MODEL != GROQ_PRIMARY_MODEL:
        models_to_try.append(GROQ_FALLBACK_MODEL)

    last_error: Optional[Exception] = None

    for index, model_name in enumerate(models_to_try):
        is_fallback = index > 0
        try:
            if is_fallback:
                logger.warning(
                    "Falling back to model '%s' after primary model "
                    "'%s' failed.",
                    model_name,
                    GROQ_PRIMARY_MODEL,
                )
            else:
                logger.info(
                    "Attempting complaint generation using model '%s'.",
                    model_name,
                )

            raw_text = _call_groq_model(client, model_name, prompt)
            parsed = _parse_and_validate(raw_text)

            logger.info(
                "Complaint generated successfully using model '%s'.", model_name
            )
            return parsed

        except ComplaintGenerationError as exc:
            last_error = exc
            logger.warning(
                "Complaint generation failed using model '%s': %s",
                model_name,
                exc,
            )
            continue

    logger.error(
        "Complaint generation failed on all configured models: %s",
        models_to_try,
    )
    raise ComplaintGenerationError(
        f"Complaint generation failed using all configured Groq models "
        f"({', '.join(models_to_try)}). Last error: {last_error}"
    ) from last_error