"""
settings.py
------------
Application settings page for GramVaani AI.

Three compact, information-card-style sections, matching the rest of
the product's visual language (Home, File Complaint, Track Complaint)
rather than reading as a developer/debug panel:
    1. Application Status (read-only) - Application Name, Version, AI
       Assistance, and Speech Recognition, laid out as labeled rows
       using the same `.gv-info-grid` pattern the Track Complaint page
       already uses for its status card, so this page shares one
       consistent "info card" language with the rest of the app
       instead of inventing its own. No internal model names,
       providers, or service versions are shown here - see
       `ai/llm/complaint_generator.py` and
       `ai/speech/speech_service.py` for that configuration; it stays
       internal implementation detail.
    2. Preferences - Application Language and Auto Delete Uploaded
       Files. Both are plain `st.session_state` values; there is no
       database.
         - "gv_app_language" -> owned by `frontend/utils/i18n.py`
           (via `get_language()`/`set_language()`). This is the ONLY
           language preference on this page: it's the interface
           language and changes every page's copy, menus, labels, and
           messages. Takes effect immediately (Streamlit reruns the
           whole script on every widget change).
         - "gv_auto_delete_files" -> read by
           `frontend/components/evidence_uploader.py` before
           replacing a previous evidence photo.
       This page previously also exposed a separate "Preferred
       Complaint Language" selector that only pre-set the default on
       `frontend/pages/file_complaint.py`'s own audio-language radio
       (`st.session_state["gv_complaint_language"]`). That selector
       has been permanently removed - now that a full interface-
       language setting exists here, a second, narrower language
       preference was redundant. `frontend/pages/file_complaint.py`'s
       radio is completely untouched by this: it still owns
       "gv_complaint_language" entirely on its own (including its own
       default), exactly as it did for any citizen who never opened
       Settings in the first place. This page no longer reads,
       writes, or resets that key anywhere.
       Changing a preference here takes effect immediately elsewhere
       in the app - these are real settings, not a cosmetic mockup.
       There is no Theme control - the app uses one fixed design
       system throughout, deliberately, so this page doesn't offer a
       toggle for something the product doesn't actually vary.
    3. System - Clear Session (wipes in-progress complaint/scheme/
       evidence/tracking data and any files saved to disk) and Restore
       Defaults (resets the preferences above only).

Layout note (Preferences / System cards):
    Earlier revisions of this page tried to visually box each card's
    *interactive* widgets by opening a `<div class="gv-card">` in one
    `st.markdown()` call, rendering real widgets (selectbox, checkbox,
    buttons) in between, then closing the div with a second, separate
    `st.markdown("</div>")` call. That doesn't actually work: each
    `st.markdown()` call renders its HTML string into its own,
    independent DOM node, so the "open" div from the first call is
    auto-closed by the browser at the end of that call's own markup,
    and the later "</div>" is an inert, orphaned tag. The visible
    symptom was a card that looked like an empty, oversized box with
    just a title, followed by the actual controls rendering unboxed,
    underneath it. The Application Status card was never affected
    (it's pure read-only HTML built and rendered in one single
    `st.markdown()` call with no interleaved widgets) - only
    Preferences and System, which both mix real Streamlit widgets into
    the card. Both now use `st.container(border=True, key="...")`
    instead: a real Streamlit container is native DOM nesting, so
    every widget rendered inside `with container:` is a genuine child
    of that container - no fragile cross-call HTML stitching. The
    `key=` gives each container a stable, targetable
    `.st-key-<key>` CSS class (Streamlit's own documented mechanism
    for styling a specific container), which `_inject_compact_settings_styles()`
    uses to make both containers match `.gv-card`'s look (border,
    radius, background, shadow, padding) instead of Streamlit's
    default container chrome.

No implementation is a placeholder: every control on this page reads
and writes real `st.session_state`, and every read-only value below
reflects the app's real, current status - not sample/demo data.
"""

import html
import shutil
from pathlib import Path

import streamlit as st

from ai.utils.complaint_tracker import SESSION_STATE_REGISTRY_KEY
from frontend.components.evidence_uploader import EVIDENCE_DIR, EVIDENCE_STATE_KEY
from frontend.components.theme import (
    COLOR_BORDER,
    COLOR_WHITE,
    RADIUS_LG,
    page_header,
)
from frontend.config.constants import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_AUTO_DELETE_FILES,
    DEFAULT_DARK_MODE,
)
from frontend.utils.i18n import DEFAULT_LANGUAGE, get_language, set_language, t

# Application Language option labels. Each language's own name for
# itself, shown as this selector's options - deliberately NOT
# translated relative to whichever language is currently active (a
# language picker conventionally shows every option in its own native
# name: "English" is always "English", never "अंग्रेज़ी", even while
# viewing the Hindi UI). So these stay local literals rather than
# keys in `frontend/utils/i18n.py`.
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

# Streamlit container keys for the Preferences and System cards (see
# module docstring "Layout note"). Each key gets its own stable
# `.st-key-<key>` CSS class - Streamlit's documented mechanism for
# styling one specific container - targeted below in
# `_inject_compact_settings_styles()`.
_PREFERENCES_CARD_KEY = "gv_settings_preferences_card"
_SYSTEM_CARD_KEY = "gv_settings_system_card"

# Directory the audio Speech-to-Text step saves temporary files to -
# mirrors ai/speech/speech_utils.py's TEMP_AUDIO_DIR. Imported as a
# path convention only (a plain, stable folder location), not as a
# private implementation detail.
_TEMP_AUDIO_DIR = Path("uploads") / "temp_audio"


def _inject_compact_settings_styles() -> None:
    """
    Tightens spacing for this page only, scoped under the
    `gv-settings-` prefix (and the two `.st-key-...` container classes
    defined above) so no other page is affected.

    The shared `.gv-card` / `.gv-info-grid` / `.gv-info-item` classes
    (defined once in `frontend/components/theme.py` and used by every
    page, e.g. Track Complaint's status card) are left completely
    untouched - this only overrides padding/margins *within* elements
    that opt into the `gv-settings-` prefixed classes, plus the two
    `st.container(border=True, key=...)` cards below, so every other
    page keeps its exact current spacing.
    """
    st.markdown(
        f"""
        <style>
            /* ---------- Shared card chrome: the plain-HTML
               Application Status card (.gv-card.gv-settings-card)
               AND the two st.container(border=True) cards below,
               targeted via their stable .st-key-... class. Both use
               identical padding/margin/radius/shadow so all three
               settings cards read as one consistent set. ---------- */
            .gv-settings-card,
            div.st-key-{_PREFERENCES_CARD_KEY},
            div.st-key-{_SYSTEM_CARD_KEY} {{
                padding: 0.95rem 1.3rem !important;
                margin-bottom: 0.7rem !important;
                border-radius: {RADIUS_LG} !important;
                border: 1px solid {COLOR_BORDER} !important;
                background-color: {COLOR_WHITE} !important;
                box-shadow: 0 1px 2px rgba(11, 31, 58, 0.04) !important;
            }}

            /* Compact, uppercase micro-heading shared by every
               settings card title - the plain <h3> inside the
               read-only card, and the markdown-rendered heading
               placed as the first element inside each st.container
               below (a real <h3> can't sit inside a Streamlit
               container's own children list, so those use this
               class directly instead of relying on ".gv-card h3"). */
            .gv-settings-card h3,
            .gv-settings-section-title {{
                display: flex;
                align-items: center;
                gap: 0.4rem;
                font-size: 0.82rem !important;
                font-weight: 700;
                letter-spacing: 0.5px;
                margin: 0 0 0.65rem 0 !important;
                text-transform: uppercase;
                opacity: 0.7;
            }}

            .gv-settings-card p {{
                margin: 0.2rem 0 !important;
            }}

            /* Compact variant of the shared .gv-info-grid/.gv-info-item
               (Track Complaint's status card) - same look, tighter
               spacing to suit a settings card rather than a full
               result card. */
            .gv-settings-card .gv-info-grid {{
                margin-top: 0.65rem;
                gap: 0.6rem;
            }}
            .gv-settings-card .gv-info-item {{
                padding: 0.55rem 0.75rem;
            }}

            /* Tightens the vertical rhythm *within* the two
               container-based cards - Streamlit's default block gap
               between widgets otherwise reads as too loose for a
               compact settings row. */
            div.st-key-{_PREFERENCES_CARD_KEY} div[data-testid="stVerticalBlock"],
            div.st-key-{_SYSTEM_CARD_KEY} div[data-testid="stVerticalBlock"] {{
                gap: 0.5rem;
            }}

            /* Pulls the Auto Delete helper caption up against the
               checkbox it explains, instead of Streamlit's default
               caption spacing reading as a floating extra line. */
            div.st-key-{_PREFERENCES_CARD_KEY} div[data-testid="stCaptionContainer"] {{
                margin-top: -0.5rem;
                margin-bottom: 0.1rem;
                opacity: 0.75;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _info_item_html(label: str, value: str) -> str:
    """
    Builds one `.gv-info-item` cell (label + value) for the
    Application Information card - the same visual language as
    Track Complaint's status grid, reused here via the shared
    `.gv-info-grid`/`.gv-info-item` classes from `theme.py` rather
    than a separate component.
    """
    return (
        '<div class="gv-info-item">'
        f'<div class="gv-info-label">{html.escape(str(label))}</div>'
        f'<div class="gv-info-value">{html.escape(str(value))}</div>'
        "</div>"
    )


def _render_app_info_card() -> None:
    """
    Renders the compact, citizen-facing "Application Information"
    card: Application Name, Version, AI Assistance, and Speech
    Recognition, each as a labeled row in a `.gv-info-grid`.
    """
    rows = "".join(
        [
            _info_item_html(t("settings.app_name_label"), APP_NAME),
            _info_item_html(t("settings.version_label"), APP_VERSION),
            _info_item_html(
                t("settings.ai_assistance_label"), t("settings.ai_assistance_value")
            ),
            _info_item_html(
                t("settings.speech_recognition_label"),
                t("settings.speech_recognition_value"),
            ),
        ]
    )
    st.markdown(
        f"""
        <div class="gv-card gv-settings-card">
            <h3>{t("settings.app_info_title")}</h3>
            <div class="gv-info-grid">{rows}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_preferences_card() -> None:
    """
    Renders the "Preferences" card: Application Language and Auto
    Delete Uploaded Files. Each control reads its current value from
    session state (falling back to the documented default) and writes
    any change straight back to the exact session-state key the rest
    of the app reads.

    Uses a real `st.container(border=True, key=...)` (see module
    docstring "Layout note") rather than a raw HTML div, so the
    selectbox/checkbox/caption below are genuine children of the card
    - not siblings rendered underneath an empty-looking box.
    """
    with st.container(border=True, key=_PREFERENCES_CARD_KEY):
        st.markdown(
            f'<h3 class="gv-settings-section-title">{t("settings.preferences_title")}</h3>',
            unsafe_allow_html=True,
        )

        # --- Application Language (frontend/utils/i18n.py) ---
        # The single language preference on this page: it drives the
        # entire interface (every page's copy, menus, labels, and
        # messages) - see the module docstring for why the old,
        # narrower "Preferred Complaint Language" selector was
        # removed. Changing it writes straight to st.session_state via
        # set_language(), then explicitly reruns: Streamlit already
        # reruns on every widget interaction, but doing this
        # explicitly (the same pattern frontend/utils/helpers.py's
        # navigate_to() already uses elsewhere) makes the
        # immediate-effect requirement unambiguous rather than relying
        # on that implicit behavior.
        current_app_language = get_language()
        if current_app_language not in _APP_LANGUAGE_OPTIONS:
            current_app_language = DEFAULT_LANGUAGE

        selected_app_language = st.selectbox(
            t("settings.app_language_label"),
            options=_APP_LANGUAGE_OPTIONS,
            index=_APP_LANGUAGE_OPTIONS.index(current_app_language),
            format_func=lambda code: _APP_LANGUAGE_NATIVE_NAMES.get(code, code),
            help=t("settings.app_language_help"),
            key="gv_app_language_select",
        )
        if selected_app_language != current_app_language:
            set_language(selected_app_language)
            st.rerun()

        # --- Auto Delete Uploaded Files ---
        auto_delete = st.checkbox(
            t("settings.auto_delete_label"),
            value=st.session_state.get(
                "gv_auto_delete_files", DEFAULT_AUTO_DELETE_FILES
            ),
            help=t("settings.auto_delete_help"),
            key="gv_auto_delete_checkbox",
        )
        st.session_state["gv_auto_delete_files"] = auto_delete
        st.caption(t("settings.auto_delete_helper_text"))


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
    features saved to disk. Preferences (Language, Auto Delete) are
    intentionally left untouched; that's what "Restore Defaults" is
    for.
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

    st.success(t("settings.clear_session_success_message"))


def _handle_restore_defaults() -> None:
    """
    Resets the two Preferences (Application Language, Auto Delete)
    back to their documented defaults.

    Also quietly resets "gv_dark_mode" to DEFAULT_DARK_MODE even
    though this page no longer exposes a Theme control - a stale
    value could otherwise persist from an older session, and the app
    is meant to render with exactly one fixed design system.
    """
    st.session_state["gv_dark_mode"] = DEFAULT_DARK_MODE
    set_language(DEFAULT_LANGUAGE)
    st.session_state["gv_auto_delete_files"] = DEFAULT_AUTO_DELETE_FILES

    # The widgets above hold their own display state under separate
    # keys - pop those too so they re-read the just-restored values
    # instead of showing what was on screen a moment ago.
    for widget_key in (
        "gv_app_language_select",
        "gv_auto_delete_checkbox",
    ):
        st.session_state.pop(widget_key, None)

    st.success(t("settings.restore_defaults_success_message"))


def _render_system_card() -> None:
    """
    Renders the "System" card: Clear Session and Restore Defaults,
    as two equal-width buttons side by side.

    Uses a real `st.container(border=True, key=...)` (see module
    docstring "Layout note") so the two-column button row is a
    genuine child of the card.
    """
    with st.container(border=True, key=_SYSTEM_CARD_KEY):
        st.markdown(
            f'<h3 class="gv-settings-section-title">{t("settings.system_title")}</h3>',
            unsafe_allow_html=True,
        )

        col_clear, col_restore = st.columns(2, gap="small")
        with col_clear:
            if st.button(
                t("settings.clear_session_button_label"),
                help=t("settings.clear_session_help"),
                use_container_width=True,
                key="gv_clear_session_button",
            ):
                _handle_clear_session()
        with col_restore:
            if st.button(
                t("settings.restore_defaults_button_label"),
                help=t("settings.restore_defaults_help"),
                use_container_width=True,
                key="gv_restore_defaults_button",
            ):
                _handle_restore_defaults()


def render() -> None:
    """Renders the Settings page."""
    _inject_compact_settings_styles()

    page_header(
        title=t("settings.title"),
        subtitle=t("settings.subtitle"),
        eyebrow=t("settings.eyebrow"),
    )

    _render_app_info_card()
    _render_preferences_card()
    _render_system_card()