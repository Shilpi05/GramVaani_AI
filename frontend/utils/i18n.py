"""
i18n.py
--------
Internationalization infrastructure for GramVaani AI's own interface
text.

This module is infrastructure ONLY at this stage: `TRANSLATIONS` is
intentionally empty for both languages, and no page has been wired up
to use `t()` yet. Nothing in the app's behavior or displayed text
changes by this module existing - it's a foundation to build on, not
a feature yet.

Scope (once populated in a later pass) - what WILL be translated:
    The application's own copy: sidebar labels, page titles/
    subtitles, section headings, card titles/text, button labels,
    form labels, placeholder text, and status/success/error messages.

Scope - what must NEVER be translated (and will never be looked up
through this module):
    - User-generated complaint text (the citizen's own spoken words,
      transcribed by Whisper)
    - AI-generated complaint content (Groq's output: complaint type,
      department, priority, summary, formal complaint)
    - Government scheme names/descriptions/eligibility text
    - Department names, whether from the LLM or the scheme knowledge
      base
    All of the above are DATA produced by the AI pipeline or the
    citizen, not this application's own copy.

Usage (once TRANSLATIONS is populated):
    from frontend.utils.i18n import t

    st.button(t("file_complaint.process_audio_button"))

The active language is stored in
`st.session_state[SESSION_STATE_LANGUAGE_KEY]`, defaulting to "en".
Changing it via `set_language()` takes effect on the very next
rerun - Streamlit reruns the whole script on every interaction, so no
other wiring is needed for a language switch to be immediate.
"""

from typing import Any, List

import streamlit as st

# ----------------------------------------------------------------------
# Language configuration
# ----------------------------------------------------------------------
DEFAULT_LANGUAGE: str = "en"
SUPPORTED_LANGUAGES: List[str] = ["en", "hi"]
SESSION_STATE_LANGUAGE_KEY: str = "gv_app_language"


def get_language() -> str:
    """
    Returns the current interface language code.

    Returns:
        The value of `st.session_state[SESSION_STATE_LANGUAGE_KEY]`,
        or `DEFAULT_LANGUAGE` ("en") if it has never been set.
    """
    return st.session_state.get(SESSION_STATE_LANGUAGE_KEY, DEFAULT_LANGUAGE)


def set_language(lang: str) -> None:
    """
    Sets the interface language for the rest of this session.

    Args:
        lang: One of `SUPPORTED_LANGUAGES` ("en" or "hi"). Silently
            ignored if not recognized, so a bad value passed in can
            never leave the app in a broken state.
    """
    if lang in SUPPORTED_LANGUAGES:
        st.session_state[SESSION_STATE_LANGUAGE_KEY] = lang


def t(key: str) -> Any:
    """
    Looks up `key` in the current language's translation table.

    Args:
        key: A translation key (convention to be used once
            `TRANSLATIONS` is populated: dotted, e.g.
            "home.hero_headline"). Most keys will map to a plain
            string, but some may map to a list/dict of structured
            content - callers that need one of those will already
            know to expect it.

    Returns:
        The translated value for the current language. Falls back to
        the English value if the key is missing for the active
        language, and falls back to the literal key string itself if
        it's missing from English too - so a missing translation is
        visibly obvious in the UI (easy to spot and fix) rather than
        silently crashing the page.

        `TRANSLATIONS` is currently empty for both languages, so every
        call to `t()` today returns the key itself unchanged - that's
        expected until the translation tables are populated in a
        later pass.
    """
    language = get_language()
    value = TRANSLATIONS.get(language, {}).get(key)
    if value is None:
        value = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key, key)
    return value


# ----------------------------------------------------------------------
# Translation tables
# ----------------------------------------------------------------------
# One dict per supported language. Intentionally empty for now (see
# module docstring) - populated in a later pass, at which point every
# key present in "en" must also be present in "hi", and vice versa, so
# `t()` never has to silently fall back mid-page.
# ----------------------------------------------------------------------
TRANSLATIONS: dict = {
    "en": {},
    "hi": {},
}