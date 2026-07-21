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
# One dict per supported language. Every key present in "en" must
# also be present in "hi", and vice versa, so `t()` never has to
# silently fall back mid-page.
#
# Populated so far: the navigation system only (sidebar nav labels,
# the app title, and the tagline) - see `frontend/components/sidebar.py`,
# the only file currently calling `t()`. Page content (Home, File
# Complaint, Scheme Finder, Track Complaint, Settings) is still
# entirely in English and untouched by this module; that's a later
# pass, not an oversight.
# ----------------------------------------------------------------------
TRANSLATIONS: dict = {
    "en": {
        # ---------- Sidebar navigation ----------
        "nav.home": "Home",
        "nav.file_complaint": "File Complaint",
        "nav.scheme_finder": "Scheme Finder",
        "nav.track_complaint": "Track Complaint",
        "nav.settings": "Settings",

        # ---------- Sidebar brand ----------
        # "AI" itself is kept as a literal, untranslated span in
        # frontend/components/sidebar.py (a fixed, globally recognized
        # acronym, styled in teal) - only the "GramVaani" part is
        # looked up here, so this key holds just that prefix.
        "sidebar.app_title_prefix": "GramVaani",
        "sidebar.tagline": "Voice of the Citizen",
    },
    "hi": {
        # ---------- Sidebar navigation ----------
        "nav.home": "होम",
        "nav.file_complaint": "शिकायत दर्ज करें",
        "nav.scheme_finder": "योजना खोजक",
        "nav.track_complaint": "शिकायत ट्रैक करें",
        "nav.settings": "सेटिंग्स",

        # ---------- Sidebar brand ----------
        "sidebar.app_title_prefix": "ग्रामवाणी",
        "sidebar.tagline": "नागरिक की आवाज़",
    },
}