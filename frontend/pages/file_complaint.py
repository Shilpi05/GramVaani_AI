"""
file_complaint.py
------------------
Complaint filing page for GramVaani AI.

This page implements two AI features end-to-end:

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
        8. The transcript is sent to Gemini
           (ai/llm/complaint_generator.py)
        9. The structured complaint (type, department, priority,
           summary, formal complaint) is displayed on screen

FUTURE INTEGRATION NOTE:
    - An image uploader -> sent to `ai/vision` for image classification
    - A submit action -> sent to `backend/services` to persist the complaint
    - Translation, scheme matching, department routing automation, etc.
      are OUT OF SCOPE for this page today and are intentionally not
      wired in.
"""

import html
from pathlib import Path
from typing import Optional
import traceback
import streamlit as st

from ai.llm.complaint_generator import ComplaintGenerationError, generate_complaint
from ai.speech.speech_service import transcribe_audio
from ai.speech.speech_utils import delete_temp_file, save_uploaded_audio
from frontend.components.theme import page_header, placeholder_card
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
    COMPLAINT_LANGUAGE_LABEL,
    COMPLAINT_PRIORITY_LABEL,
    COMPLAINT_RESULT_CARD_TITLE,
    COMPLAINT_SUMMARY_LABEL,
    COMPLAINT_TYPE_LABEL,
    FILE_COMPLAINT_EYEBROW,
    FILE_COMPLAINT_IMAGE_CARD_TEXT,
    FILE_COMPLAINT_IMAGE_CARD_TITLE,
    FILE_COMPLAINT_PLACEHOLDER,
    FILE_COMPLAINT_SUBTITLE,
    FILE_COMPLAINT_TITLE,
    FILE_COMPLAINT_VOICE_CARD_TEXT,
    FILE_COMPLAINT_VOICE_CARD_TITLE,
    GENERATE_COMPLAINT_BUTTON_LABEL,
    LANGUAGE_CODE_MAP,
    LANGUAGE_OPTIONS,
    PROCESS_AUDIO_BUTTON_LABEL,
    TRANSCRIPT_CARD_TITLE,
)

# Session-state keys used to persist results across reruns so they
# stay visible after their respective button clicks complete.
_TRANSCRIPT_STATE_KEY: str = "gv_recognized_speech"
_COMPLAINT_STATE_KEY: str = "gv_generated_complaint"


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


def _handle_generate_complaint(transcript: Optional[str]) -> None:
    """
    Runs the Complaint Generation flow: sends the transcript to
    Gemini via `ai/llm/complaint_generator.py` and stores the
    structured result for display.

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
            print(traceback.format_exc())   # full traceback in terminal
            st.exception(exc)               # full exception in the UI
            return

    st.session_state[_COMPLAINT_STATE_KEY] = complaint


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
    if st.button(GENERATE_COMPLAINT_BUTTON_LABEL, use_container_width=True):
        _handle_generate_complaint(transcript)


def _render_complaint_result_if_available() -> None:
    """Renders the generated structured complaint in a styled card, if one exists."""
    complaint = st.session_state.get(_COMPLAINT_STATE_KEY)
    if not complaint:
        return

    # Escape every field before rendering as HTML - the values come
    # from an LLM response and should never be trusted as safe markup.
    complaint_type = html.escape(str(complaint.get("complaint_type", "")))
    department = html.escape(str(complaint.get("department", "")))
    priority = html.escape(str(complaint.get("priority", "")))
    summary = html.escape(str(complaint.get("summary", "")))
    formal_complaint = html.escape(str(complaint.get("formal_complaint", "")))

    st.write("")
    st.markdown(
        f"""
        <div class="gv-card">
            <h3>{COMPLAINT_RESULT_CARD_TITLE}</h3>
            <p><strong>{COMPLAINT_TYPE_LABEL}:</strong> {complaint_type}</p>
            <p><strong>{COMPLAINT_DEPARTMENT_LABEL}:</strong> {department}</p>
            <p><strong>{COMPLAINT_PRIORITY_LABEL}:</strong> {priority}</p>
            <p><strong>{COMPLAINT_SUMMARY_LABEL}:</strong> {summary}</p>
            <p><strong>{COMPLAINT_FORMAL_TEXT_LABEL}:</strong><br>{formal_complaint}</p>
        </div>
        """,
        unsafe_allow_html=True,
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

        if st.button(PROCESS_AUDIO_BUTTON_LABEL, use_container_width=True):
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

    # --- Display the recognized speech + "Generate Complaint" trigger ---
    _render_transcript_if_available()

    # --- Display the generated structured complaint, if any ---
    _render_complaint_result_if_available()

    st.write("")
    st.divider()
    placeholder_card(icon="📝", text=FILE_COMPLAINT_PLACEHOLDER)
