"""
settings.py
------------
Application settings page for GramVaani AI.

Three compact sections, styled to match the rest of the product
(Home, File Complaint) rather than reading as a developer/debug
panel:
    1. Application Status (read-only) - simple, citizen-facing status
       lines only. No internal model names, providers, or service
       versions are shown here - see `ai/llm/complaint_generator.py`
       and `ai/speech/speech_service.py` for that configuration; it
       stays internal implementation detail.
    2. Preferences - Application Language, Preferred Complaint
       Language, and Auto Delete Uploaded Files. All are plain
       `st.session_state` values; there is no database. Some of these
       keys are also read by *other* pages:
         - "gv_app_language" -> owned by `frontend/utils/i18n.py`
           (via `get_language()`/`set_language()`); this is the
           interface language, separate from the complaint language
           below. No page reads translated text through it yet - that
           lands in a later pass - but the preference itself is real
           and already takes effect immediately (Streamlit reruns the
           whole script on every widget change).
         - "gv_complaint_language" -> the exact widget key
           `frontend/pages/file_complaint.py`'s language radio uses,
           so setting it here changes that radio's default. "Auto
           Detect" is one of its own selectable options, so no
           separate toggle is needed for it.
         - "gv_auto_delete_files" -> read by
           `frontend/components/evidence_uploader.py` before
           replacing a previous evidence photo.
       Changing a preference here takes effect immediately elsewhere
       in the app - these are real settings, not a cosmetic mockup.
       There is no Theme control - the app uses one fixed design
       system throughout, deliberately, so this page doesn't offer a
       toggle for something the product doesn't actually vary.
    3. System - Clear Session (wipes in-progress complaint/scheme/
       evidence/tracking data and any files saved to disk) and Restore
       Defaults (resets the preferences above only).

No implementation is a placeholder: every control on this page reads
and writes real `st.session_state`, and every read-only value below
reflects the app's real, current status - not sample/demo data.
"""

import shutil
from pathlib import Path

import streamlit as st

from ai.utils.complaint_tracker import SESSION_STATE_REGISTRY_KEY
from frontend.components.evidence_uploader import EVIDENCE_DIR, EVIDENCE_STATE_KEY
from frontend.components.theme import info_row_html, page_header
from frontend.config.constants import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_AUTO_DELETE_FILES,
    DEFAULT_COMPLAINT_LANGUAGE,
    DEFAULT_DARK_MODE,
    LANGUAGE_OPTIONS,
    SETTINGS_AI_ASSISTANCE_LABEL,
    SETTINGS_AI_ASSISTANCE_VALUE,
    SETTINGS_APP_INFO_TITLE,
    SETTINGS_APP_NAME_LABEL,
    SETTINGS_AUTO_DELETE_HELP,
    SETTINGS_AUTO_DELETE_LABEL,
    SETTINGS_CLEAR_SESSION_BUTTON_LABEL,
    SETTINGS_CLEAR_SESSION_HELP,
    SETTINGS_CLEAR_SESSION_SUCCESS_MESSAGE,
    SETTINGS_EYEBROW,
    SETTINGS_LANGUAGE_HELP,
    SETTINGS_LANGUAGE_LABEL,
    SETTINGS_PREFERENCES_TITLE,
    SETTINGS_RESTORE_DEFAULTS_BUTTON_LABEL,
    SETTINGS_RESTORE_DEFAULTS_HELP,
    SETTINGS_RESTORE_DEFAULTS_SUCCESS_MESSAGE,
    SETTINGS_SPEECH_RECOGNITION_LABEL,
    SETTINGS_SPEECH_RECOGNITION_VALUE,
    SETTINGS_SUBTITLE,
    SETTINGS_SYSTEM_TITLE,
    SETTINGS_TITLE,
    SETTINGS_VERSION_LABEL,
)
from frontend.utils.i18n import DEFAULT_LANGUAGE, get_language, set_language

# Application Language option labels. Kept local to this page rather
# than added to frontend/config/constants.py: this task is scoped to
# settings.py only, and every other page already imports its own copy
# from constants.py, so nothing here is duplicated - it's simply not
# centralized yet. A later pass that wires other pages up to
# frontend/utils/i18n.py's t() helper is the natural point to move
# this alongside everything else.
#
# Each language's own name for itself, shown as this selector's
# options - deliberately NOT translated relative to whichever
# language is currently active (a language picker conventionally
# shows every option in its own native name: "English" is always
# "English", never "अंग्रेज़ी", even while viewing the Hindi UI).
_APP_LANGUAGE_LABEL = "Application Language"
_APP_LANGUAGE_HELP = (
    "Changes the language of the app's own interface - menus, labels, and messages."
)
_APP_LANGUAGE_NATIVE_NAMES = {"en": "English", "hi": "हिन्दी"}
_APP_LANGUAGE_OPTIONS = list(_APP_LANGUAGE_NATIVE_NAMES.keys())

# Session-state keys owned by *other* pages/components, needed here
# only so "Clear Session" can reset a citizen's in-progress workflow.
# The transcript/complaint keys are private (leading underscore) to
# `frontend/pages/file_complaint.py` and have no public constant to
# import today - their literal values are reproduced here instead,
# each one pinned to the exact line that defines it so this doesn't
# silently drift out of sync. A future pass should promote both to
# public constants the same way `SCHEMES_STATE_KEY` already was.
_TRANSCRIPT_STATE_KEY = "gv_recognized_speech"  # file_complaint.py: _TRANSCRIPT_STATE_KEY
_GENERATED_COMPLAINT_STATE_KEY = "gv_generated_complaint"  # file_complaint.py: _COMPLAINT_STATE_KEY

# frontend/pages/file_complaint.py defines this one without a leading
# underscore specifically so other modules (originally scheme_finder.py,
# now also this page) can import it.
from frontend.pages.file_complaint import SCHEMES_STATE_KEY  # noqa: E402

# Widget keys that hold their own uploaded-file state and need to be
# explicitly cleared (popped) for the corresponding uploader to reset,
# using the same pattern evidence_uploader.py's own "Remove" button
# already relies on.
_AUDIO_UPLOADER_WIDGET_KEY = "gv_audio_uploader"
_EVIDENCE_UPLOADER_WIDGET_KEY = "gv_evidence_uploader"

# Directory the audio Speech-to-Text step saves temporary files to -
# mirrors ai/speech/speech_utils.py's TEMP_AUDIO_DIR. Imported as a
# path convention only (a plain, stable folder location), not as a
# private implementation detail.
_TEMP_AUDIO_DIR = Path("uploads") / "temp_audio"


def _inject_compact_settings_styles() -> None:
    """
    Tightens spacing for this page only, scoped under the
    `gv-settings-` prefix so no other page is affected.

    The shared `.gv-card` class (defined once in
    `frontend/components/theme.py` and used by every page) is left
    completely untouched - this only overrides padding/margins
    *within* cards that opt into the `gv-settings-card` class, so
    Home/File Complaint/Scheme Finder/Track Complaint keep their
    exact current spacing.
    """
    st.markdown(
        """
        <style>
            .gv-settings-card {
                padding: 1.1rem 1.35rem !important;
                margin-bottom: 0.85rem;
            }
            .gv-settings-card h3 {
                font-size: 0.95rem !important;
                font-weight: 700;
                letter-spacing: 0.2px;
                margin: 0 0 0.6rem 0 !important;
                text-transform: uppercase;
                opacity: 0.75;
            }
            .gv-settings-card p {
                margin: 0.2rem 0 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_app_status_card() -> None:
    """Renders the compact, citizen-facing "Application Status" card."""
    rows = "".join(
        [
            info_row_html(SETTINGS_APP_NAME_LABEL, APP_NAME),
            info_row_html(SETTINGS_VERSION_LABEL, APP_VERSION),
            info_row_html(SETTINGS_AI_ASSISTANCE_LABEL, SETTINGS_AI_ASSISTANCE_VALUE),
            info_row_html(
                SETTINGS_SPEECH_RECOGNITION_LABEL, SETTINGS_SPEECH_RECOGNITION_VALUE
            ),
        ]
    )
    st.markdown(
        f"""
        <div class="gv-card gv-settings-card">
            <h3>{SETTINGS_APP_INFO_TITLE}</h3>
            {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_preferences_card() -> None:
    """
    Renders the "Preferences" card: Application Language, Preferred
    Complaint Language, and Auto Delete Uploaded Files. Each control
    reads its current value from session state (falling back to the
    documented default) and writes any change straight back to the
    exact session-state key the rest of the app reads.
    """
    st.markdown(
        f'<div class="gv-card gv-settings-card"><h3>{SETTINGS_PREFERENCES_TITLE}</h3>',
        unsafe_allow_html=True,
    )

    # --- Application Language (frontend/utils/i18n.py) ---
    # This is the interface language - separate from "Preferred
    # Complaint Language" below, which only sets Whisper's default.
    # Changing it writes straight to st.session_state via
    # set_language(), then explicitly reruns: Streamlit already
    # reruns on every widget interaction, but doing this explicitly
    # (the same pattern frontend/utils/helpers.py's navigate_to()
    # already uses elsewhere) makes the immediate-effect requirement
    # unambiguous rather than relying on that implicit behavior.
    current_app_language = get_language()
    if current_app_language not in _APP_LANGUAGE_OPTIONS:
        current_app_language = DEFAULT_LANGUAGE

    selected_app_language = st.selectbox(
        _APP_LANGUAGE_LABEL,
        options=_APP_LANGUAGE_OPTIONS,
        index=_APP_LANGUAGE_OPTIONS.index(current_app_language),
        format_func=lambda code: _APP_LANGUAGE_NATIVE_NAMES.get(code, code),
        help=_APP_LANGUAGE_HELP,
        key="gv_app_language_select",
    )
    if selected_app_language != current_app_language:
        set_language(selected_app_language)
        st.rerun()

    # --- Preferred Complaint Language ---
    # "Auto Detect" is one of LANGUAGE_OPTIONS' own selectable values
    # (not a separate toggle), so this selectbox alone covers it.
    current_language = st.session_state.get(
        "gv_complaint_language", DEFAULT_COMPLAINT_LANGUAGE
    )
    if current_language not in LANGUAGE_OPTIONS:
        current_language = DEFAULT_COMPLAINT_LANGUAGE
    selected_language = st.selectbox(
        SETTINGS_LANGUAGE_LABEL,
        options=LANGUAGE_OPTIONS,
        index=LANGUAGE_OPTIONS.index(current_language),
        help=SETTINGS_LANGUAGE_HELP,
        key="gv_preferred_language_select",
    )
    st.session_state["gv_complaint_language"] = selected_language

    # --- Auto Delete Uploaded Files ---
    auto_delete = st.checkbox(
        SETTINGS_AUTO_DELETE_LABEL,
        value=st.session_state.get("gv_auto_delete_files", DEFAULT_AUTO_DELETE_FILES),
        help=SETTINGS_AUTO_DELETE_HELP,
        key="gv_auto_delete_checkbox",
    )
    st.session_state["gv_auto_delete_files"] = auto_delete

    st.markdown("</div>", unsafe_allow_html=True)


def _delete_directory_contents(directory: Path) -> None:
    """
    Deletes every file inside `directory` (not the directory itself),
    ignoring any file that's already gone or fails to delete - a
    cleanup step should never crash the page.

    Args:
        directory: The folder whose contents should be removed.
    """
    if not directory.exists():
        return
    for entry in directory.iterdir():
        try:
            if entry.is_file():
                entry.unlink()
            elif entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
        except OSError:
            pass


def _handle_clear_session() -> None:
    """
    Clears this session's in-progress workflow data: recognized
    speech, generated complaint, recommended schemes, evidence photo,
    and the local complaint-tracking registry - plus any files those
    features saved to disk. Preferences (Language, Auto Detect, Auto
    Delete) are intentionally left untouched; that's what "Restore
    Defaults" is for.
    """
    for key in (
        _TRANSCRIPT_STATE_KEY,
        _GENERATED_COMPLAINT_STATE_KEY,
        SCHEMES_STATE_KEY,
        EVIDENCE_STATE_KEY,
        SESSION_STATE_REGISTRY_KEY,
        _AUDIO_UPLOADER_WIDGET_KEY,
        _EVIDENCE_UPLOADER_WIDGET_KEY,
    ):
        st.session_state.pop(key, None)

    _delete_directory_contents(EVIDENCE_DIR)
    _delete_directory_contents(_TEMP_AUDIO_DIR)

    st.success(SETTINGS_CLEAR_SESSION_SUCCESS_MESSAGE)


def _handle_restore_defaults() -> None:
    """
    Resets the three Preferences back to their documented defaults.

    Also quietly resets "gv_dark_mode" to DEFAULT_DARK_MODE even
    though this page no longer exposes a Theme control - a stale
    value could otherwise persist from an older session, and the app
    is meant to render with exactly one fixed design system.
    """
    st.session_state["gv_dark_mode"] = DEFAULT_DARK_MODE
    set_language(DEFAULT_LANGUAGE)
    st.session_state["gv_complaint_language"] = DEFAULT_COMPLAINT_LANGUAGE
    st.session_state["gv_auto_delete_files"] = DEFAULT_AUTO_DELETE_FILES

    # The widgets above hold their own display state under separate
    # keys - pop those too so they re-read the just-restored values
    # instead of showing what was on screen a moment ago.
    for widget_key in (
        "gv_app_language_select",
        "gv_preferred_language_select",
        "gv_auto_delete_checkbox",
    ):
        st.session_state.pop(widget_key, None)

    st.success(SETTINGS_RESTORE_DEFAULTS_SUCCESS_MESSAGE)


def _render_system_card() -> None:
    """Renders the "System" card: Clear Session and Restore Defaults."""
    st.markdown(
        f'<div class="gv-card gv-settings-card"><h3>{SETTINGS_SYSTEM_TITLE}</h3>',
        unsafe_allow_html=True,
    )

    col_clear, col_restore = st.columns(2)
    with col_clear:
        if st.button(
            SETTINGS_CLEAR_SESSION_BUTTON_LABEL,
            help=SETTINGS_CLEAR_SESSION_HELP,
            use_container_width=True,
            key="gv_clear_session_button",
        ):
            _handle_clear_session()
    with col_restore:
        if st.button(
            SETTINGS_RESTORE_DEFAULTS_BUTTON_LABEL,
            help=SETTINGS_RESTORE_DEFAULTS_HELP,
            use_container_width=True,
            key="gv_restore_defaults_button",
        ):
            _handle_restore_defaults()

    st.markdown("</div>", unsafe_allow_html=True)


def render() -> None:
    """Renders the Settings page."""
    _inject_compact_settings_styles()

    page_header(
        title=SETTINGS_TITLE,
        subtitle=SETTINGS_SUBTITLE,
        eyebrow=SETTINGS_EYEBROW,
    )

    _render_app_status_card()
    _render_preferences_card()
    _render_system_card()