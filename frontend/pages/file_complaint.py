"""
file_complaint.py
------------------
Complaint filing page for GramVaani AI.

This page implements six AI/utility features end-to-end:

    Speech-to-Text (ai/speech):
        1. Citizen uploads an audio file (wav / mp3 / m4a)
        2. Citizen selects a complaint language
        3. Citizen clicks "Process Audio"
        4. Audio is saved temporarily (ai/speech/speech_utils.py)
        5. Whisper transcribes it (ai/speech/speech_service.py)
        6. The recognized speech is displayed on screen

    Complaint Generation (ai/llm):
        7. Citizen clicks "Generate Complaint" (shown once a
           transcript exists)
        8. The transcript is sent to Groq
           (ai/llm/complaint_generator.py)
        9. The structured complaint (type, department, priority,
           summary, formal complaint) is displayed on screen

    Complaint ID Generation (ai/utils):
        10. Immediately after a complaint is generated, a unique
            Complaint ID in the format GV-YYYYMMDD-NNNNN is created
            (ai/utils/complaint_id.py) - entirely offline, no
            external calls - and attached to the complaint dict as
            "complaint_id"
        11. The Complaint ID is shown at the top of the generated
            complaint card

    Government Scheme Recommendation (ai/schemes):
        12. The complaint's type/department/summary are matched
            against a local, offline knowledge base
            (ai/schemes/scheme_recommender.py) - no external API
            calls involved, and stored in session state
        13. The matched schemes (or "no direct scheme found") are
            displayed on the dedicated "Scheme Finder" page
            (frontend/pages/scheme_finder.py), not here - this page
            is only responsible for computing them, since that's
            where the complaint data they're derived from exists

    PDF Export (ai/utils/pdf_generator.py):
        14. A "Download Complaint" button renders a professionally
            formatted PDF (via `reportlab`) containing the Complaint
            ID, date, type, department, priority, summary, formal
            complaint, and recommended schemes - built entirely
            offline, no external calls

    Complaint Tracking Registration (ai/utils/complaint_tracker.py):
        15. Every generated complaint is registered into a mock,
            session-only tracking registry (no database, no
            authentication) so its status can later be looked up by
            Complaint ID on the "Track Complaint" page

FUTURE INTEGRATION NOTE:
    - An image uploader -> sent to `ai/vision` for image classification
    - Translation, department routing automation, etc. are OUT OF
      SCOPE for this page today and are intentionally not wired in.
"""

import html
import traceback
from datetime import date
from pathlib import Path
from typing import Optional

import streamlit as st

from ai.llm.complaint_generator import generate_complaint
from ai.schemes.scheme_recommender import recommend_schemes
from ai.speech.speech_service import transcribe_audio
from ai.speech.speech_utils import delete_temp_file, save_uploaded_audio
from ai.utils.complaint_id import generate_complaint_id
from ai.utils.complaint_tracker import SESSION_STATE_REGISTRY_KEY as TRACKER_REGISTRY_KEY
from ai.utils.complaint_tracker import register_complaint
from ai.utils.pdf_generator import generate_complaint_pdf
from frontend.components.evidence_uploader import (
    EVIDENCE_STATE_KEY,
    render_evidence_upload_section,
)
from frontend.components.theme import (
    department_badge_html,
    page_header,
    priority_badge_html,
)
from frontend.config.constants import (
    AUDIO_EMPTY_FILE_WARNING,
    AUDIO_NO_FILE_WARNING,
    AUDIO_NO_SPEECH_DETECTED_WARNING,
    AUDIO_PROCESSING_MESSAGE,
    AUDIO_SUPPORTED_FORMATS,
    AUDIO_TRANSCRIPTION_FAILED_ERROR,
    AUDIO_UNSUPPORTED_FORMAT_ERROR,
    AUDIO_UPLOADER_HELP,
    AUDIO_UPLOADER_LABEL,
    COMPLAINT_DEPARTMENT_LABEL,
    COMPLAINT_EMPTY_TRANSCRIPT_WARNING,
    COMPLAINT_FORMAL_TEXT_LABEL,
    COMPLAINT_GENERATION_PROCESSING_MESSAGE,
    COMPLAINT_ID_LABEL,
    COMPLAINT_LANGUAGE_LABEL,
    COMPLAINT_PRIORITY_LABEL,
    COMPLAINT_RESULT_CARD_TITLE,
    COMPLAINT_SUMMARY_LABEL,
    COMPLAINT_TYPE_LABEL,
    DOWNLOAD_COMPLAINT_BUTTON_LABEL,
    EVIDENCE_ATTACHED_NOTE,
    FILE_COMPLAINT_EYEBROW,
    FILE_COMPLAINT_IMAGE_CARD_TEXT,
    FILE_COMPLAINT_IMAGE_CARD_TITLE,
    FILE_COMPLAINT_SUBTITLE,
    FILE_COMPLAINT_TITLE,
    FILE_COMPLAINT_VOICE_CARD_TEXT,
    FILE_COMPLAINT_VOICE_CARD_TITLE,
    GENERATE_COMPLAINT_BUTTON_LABEL,
    LANGUAGE_CODE_MAP,
    LANGUAGE_OPTIONS,
    PDF_GENERATION_FAILED_ERROR,
    PROCESS_AUDIO_BUTTON_LABEL,
    SCHEME_NO_MATCH_MESSAGE,
    TRANSCRIPT_CARD_TITLE,
)

# Session-state keys used to persist results across reruns so they
# stay visible after their respective button clicks complete.
_TRANSCRIPT_STATE_KEY: str = "gv_recognized_speech"
_COMPLAINT_STATE_KEY: str = "gv_generated_complaint"

# Public (no leading underscore) because `frontend/pages/scheme_finder.py`
# reads this key to display the schemes computed here - same pattern
# as `ai/utils/complaint_tracker.SESSION_STATE_REGISTRY_KEY`, which
# other pages already import rather than redefining the key locally.
SCHEMES_STATE_KEY: str = "gv_recommended_schemes"


def _handle_process_audio(uploaded_file, language_code: Optional[str]) -> None:
    """
    Runs the end-to-end Speech-to-Text flow for one uploaded audio file:
    save temporarily -> transcribe -> clean up -> store result for display.

    Args:
        uploaded_file: The Streamlit `UploadedFile` returned by the
            audio uploader widget, or None if nothing was uploaded.
        language_code: Whisper language code selected by the citizen
            ("hi", "en"), or None for auto-detect.
    """
    # --- Validation: no file uploaded ---
    if uploaded_file is None:
        st.warning(AUDIO_NO_FILE_WARNING)
        return

    # --- Validation: empty file ---
    if uploaded_file.size == 0:
        st.warning(AUDIO_EMPTY_FILE_WARNING)
        return

    temp_audio_path: Optional[Path] = None

    with st.spinner(AUDIO_PROCESSING_MESSAGE):
        try:
            # Step 1: save the uploaded audio to a temporary file.
            # save_uploaded_audio() also validates the extension and
            # raises ValueError for unsupported formats / empty content.
            temp_audio_path = save_uploaded_audio(uploaded_file)

            # Step 2: run Whisper transcription on the saved file,
            # using the citizen's selected complaint language.
            transcript = transcribe_audio(temp_audio_path, language=language_code)

        except ValueError:
            # Raised by save_uploaded_audio() for unsupported extensions
            # or empty file content.
            st.error(AUDIO_UNSUPPORTED_FORMAT_ERROR)
            return
        except (FileNotFoundError, RuntimeError):
            # Raised by transcribe_audio() for missing files or any
            # Whisper/ffmpeg-level transcription failure.
            st.error(AUDIO_TRANSCRIPTION_FAILED_ERROR)
            return
        finally:
            # Step 3: always clean up the temporary audio file,
            # whether transcription succeeded or failed.
            delete_temp_file(temp_audio_path)

    # --- No speech detected in an otherwise valid audio file ---
    if not transcript:
        st.warning(AUDIO_NO_SPEECH_DETECTED_WARNING)
        st.session_state.pop(_TRANSCRIPT_STATE_KEY, None)
        return

    # Store the transcript so it renders below, and survives reruns
    # triggered by other widgets on this page. A fresh transcript
    # invalidates any previously generated complaint.
    st.session_state[_TRANSCRIPT_STATE_KEY] = transcript
    st.session_state.pop(_COMPLAINT_STATE_KEY, None)
    st.session_state.pop(SCHEMES_STATE_KEY, None)


def _handle_generate_complaint(transcript: Optional[str]) -> None:
    """
    Runs the Complaint Generation flow: sends the transcript to Groq
    via `ai/llm/complaint_generator.py`, attaches a freshly generated
    Complaint ID (`ai/utils/complaint_id.py`), stores the structured
    result for display, then looks up matching government schemes
    via `ai/schemes/scheme_recommender.py` and stores those too.

    Args:
        transcript: The recognized speech to generate a complaint
            from, or None/empty if no transcript is available yet.
    """
    # --- Validation: no transcript available yet ---
    if not transcript or not transcript.strip():
        st.warning(COMPLAINT_EMPTY_TRANSCRIPT_WARNING)
        return

    with st.spinner(COMPLAINT_GENERATION_PROCESSING_MESSAGE):
        try:
            complaint = generate_complaint(transcript)
        except ValueError:
            # Raised by generate_complaint() for an empty/blank transcript.
            st.warning(COMPLAINT_EMPTY_TRANSCRIPT_WARNING)
            return
        except Exception as exc:
            # DEBUG MODE: surface the full exception instead of a
            # generic message, so the real cause (auth error, rate
            # limit, network timeout, etc.) is visible during
            # development. Also print the full traceback to the
            # terminal for easier debugging.
            print(traceback.format_exc())
            st.exception(exc)
            return

    # --- Complaint ID Generation (ai/utils) ---
    # Runs entirely offline (date + random digits, no external calls).
    # Attached to the complaint dict returned by generate_complaint()
    # here, at the integration layer - the complaint generation logic
    # in ai/llm/complaint_generator.py itself is untouched.
    complaint["complaint_id"] = generate_complaint_id()
    complaint["generated_date"] = date.today().strftime("%d %B %Y")

    st.session_state[_COMPLAINT_STATE_KEY] = complaint

    # --- Complaint Tracking Registration (ai/utils/complaint_tracker) ---
    # Mock, session-only tracking - no database, no authentication.
    # Registers this complaint so it can later be looked up by ID on
    # the Track Complaint page. Never raises - a registration failure
    # should never block the complaint the citizen just generated
    # from being shown.
    try:
        tracking_registry = st.session_state.setdefault(
            TRACKER_REGISTRY_KEY, {}
        )
        register_complaint(tracking_registry, complaint)
    except Exception:  # noqa: BLE001
        print(traceback.format_exc())

    # --- Government Scheme Recommendation (ai/schemes) ---
    # Runs entirely offline against a local knowledge base, using the
    # freshly generated complaint's type/department/summary. Never
    # raises - a lookup failure should never block the complaint the
    # citizen just generated from being shown, so any unexpected
    # error here is logged and treated as "no schemes found" rather
    # than surfaced to the citizen.
    try:
        schemes = recommend_schemes(
            complaint_type=complaint.get("complaint_type", ""),
            department=complaint.get("department", ""),
            summary=complaint.get("summary", ""),
        )
    except Exception:  # noqa: BLE001
        print(traceback.format_exc())
        schemes = SCHEME_NO_MATCH_MESSAGE

    st.session_state[SCHEMES_STATE_KEY] = schemes


def _render_transcript_if_available() -> None:
    """Renders the recognized speech in a styled card, if one exists."""
    transcript = st.session_state.get(_TRANSCRIPT_STATE_KEY)
    if not transcript:
        return

    # Escape the transcript before rendering as HTML so any special
    # characters (<, >, &) in the recognized speech don't break the
    # card markup or get interpreted as HTML.
    safe_transcript = html.escape(transcript)

    st.write("")
    st.markdown(
        f"""
        <div class="gv-card">
            <h3>{TRANSCRIPT_CARD_TITLE}</h3>
            <p>{safe_transcript}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # "Generate Complaint" only appears once a transcript exists.
    st.write("")
    if st.button(
        GENERATE_COMPLAINT_BUTTON_LABEL,
        use_container_width=True,
        type="primary",
        key="gv_generate_complaint_button",
    ):
        _handle_generate_complaint(transcript)


def _render_complaint_result_if_available() -> None:
    """Renders the generated structured complaint in a styled card, if one exists."""
    complaint = st.session_state.get(_COMPLAINT_STATE_KEY)
    if not complaint:
        return

    # Escape every field before rendering as HTML - the values come
    # from an LLM response and should never be trusted as safe markup.
    # Department/priority are rendered as badges via theme.py helpers,
    # which handle their own escaping internally.
    complaint_id = html.escape(str(complaint.get("complaint_id", "")))
    complaint_type = html.escape(str(complaint.get("complaint_type", "")))
    department_badge = department_badge_html(complaint.get("department", ""))
    priority_badge = priority_badge_html(complaint.get("priority", ""))
    summary = html.escape(str(complaint.get("summary", "")))
    formal_complaint = html.escape(str(complaint.get("formal_complaint", "")))

    # Evidence photo, if the citizen attached one via
    # frontend/components/evidence_uploader.py. Purely a note that a
    # photo exists (filename only) - the image itself is never
    # inspected or classified.
    evidence = st.session_state.get(EVIDENCE_STATE_KEY)
    evidence_row = ""
    if evidence:
        evidence_filename = html.escape(str(evidence.get("filename", "")))
        evidence_row = (
            f"<p>{EVIDENCE_ATTACHED_NOTE} <strong>{evidence_filename}</strong></p>"
        )

    st.write("")
    st.markdown(
        f"""
        <div class="gv-card">
            <h3>{COMPLAINT_RESULT_CARD_TITLE}</h3>
            <p><strong>{COMPLAINT_ID_LABEL}:</strong> {complaint_id}</p>
            <p><strong>{COMPLAINT_TYPE_LABEL}:</strong> {complaint_type}</p>
            <p><strong>{COMPLAINT_DEPARTMENT_LABEL}:</strong> {department_badge}</p>
            <p><strong>{COMPLAINT_PRIORITY_LABEL}:</strong> {priority_badge}</p>
            <p><strong>{COMPLAINT_SUMMARY_LABEL}:</strong> {summary}</p>
            <p><strong>{COMPLAINT_FORMAL_TEXT_LABEL}:</strong><br>{formal_complaint}</p>
            {evidence_row}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_download_button_if_available() -> None:
    """
    Renders a "Download Complaint" button that generates a
    professionally formatted PDF (via `ai/utils/pdf_generator.py`)
    from the currently generated complaint and its recommended
    schemes, if a complaint has been generated.

    The PDF is (re)built on every rerun from session state - cheap
    and deterministic - rather than cached, so it always reflects the
    latest complaint/schemes in view. A PDF generation failure is
    logged and shown as a friendly error; it never breaks the rest of
    the page.
    """
    complaint = st.session_state.get(_COMPLAINT_STATE_KEY)
    if not complaint:
        return

    schemes = st.session_state.get(SCHEMES_STATE_KEY)

    try:
        pdf_bytes = generate_complaint_pdf(complaint, schemes)
    except Exception:  # noqa: BLE001
        print(traceback.format_exc())
        st.error(PDF_GENERATION_FAILED_ERROR)
        return

    complaint_id = str(complaint.get("complaint_id", "")).strip()
    file_name = f"{complaint_id}.pdf" if complaint_id else "gramvaani_complaint.pdf"

    st.write("")
    st.download_button(
        label=DOWNLOAD_COMPLAINT_BUTTON_LABEL,
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf",
        use_container_width=True,
        type="primary",
        key="gv_download_complaint_pdf",
    )


def render() -> None:
    """Renders the File Complaint page."""
    page_header(
        title=FILE_COMPLAINT_TITLE,
        subtitle=FILE_COMPLAINT_SUBTITLE,
        eyebrow=FILE_COMPLAINT_EYEBROW,
    )

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            f"""
            <div class="gv-card">
                <h3>{FILE_COMPLAINT_VOICE_CARD_TITLE}</h3>
                <p>{FILE_COMPLAINT_VOICE_CARD_TEXT}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        # --- Speech-to-Text: language choice + audio uploader + process button ---
        selected_language_label = st.radio(
            label=COMPLAINT_LANGUAGE_LABEL,
            options=LANGUAGE_OPTIONS,
            horizontal=True,
            key="gv_complaint_language",
        )

        uploaded_audio = st.file_uploader(
            label=AUDIO_UPLOADER_LABEL,
            type=AUDIO_SUPPORTED_FORMATS,
            help=AUDIO_UPLOADER_HELP,
            key="gv_audio_uploader",
        )

        if st.button(
            PROCESS_AUDIO_BUTTON_LABEL,
            use_container_width=True,
            type="primary",
            key="gv_process_audio_button",
        ):
            language_code = LANGUAGE_CODE_MAP[selected_language_label]
            _handle_process_audio(uploaded_audio, language_code)

    with col_right:
        st.markdown(
            f"""
            <div class="gv-card">
                <h3>{FILE_COMPLAINT_IMAGE_CARD_TITLE}</h3>
                <p>{FILE_COMPLAINT_IMAGE_CARD_TEXT}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        # --- Evidence photo upload (frontend/components/evidence_uploader.py) ---
        render_evidence_upload_section()

    # --- Display the recognized speech + "Generate Complaint" trigger ---
    _render_transcript_if_available()

    # --- Display the generated structured complaint, if any ---
    _render_complaint_result_if_available()

    # --- Offer a PDF download of the complaint + schemes, if any ---
    _render_download_button_if_available()