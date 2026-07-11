"""
file_complaint.py
------------------
Complaint filing page for GramVaani AI.

Today this page implements ONLY the Speech-to-Text feature:
    1. Citizen uploads an audio file (wav / mp3 / m4a)
    2. Citizen clicks "Process Audio"
    3. Audio is saved temporarily (ai/speech/speech_utils.py)
    4. Whisper transcribes it (ai/speech/speech_service.py)
    5. The recognized speech is displayed on screen

FUTURE INTEGRATION NOTE:
    - An image uploader -> sent to `ai/vision` for image classification
    - A submit action -> sent to `backend/services` to persist the complaint
    - Translation, LLM categorization, scheme matching etc. are OUT OF
      SCOPE for this page today and are intentionally not wired in.
"""

import html
from pathlib import Path
from typing import Optional

import streamlit as st

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
    FILE_COMPLAINT_EYEBROW,
    FILE_COMPLAINT_IMAGE_CARD_TEXT,
    FILE_COMPLAINT_IMAGE_CARD_TITLE,
    FILE_COMPLAINT_PLACEHOLDER,
    FILE_COMPLAINT_SUBTITLE,
    FILE_COMPLAINT_TITLE,
    FILE_COMPLAINT_VOICE_CARD_TEXT,
    FILE_COMPLAINT_VOICE_CARD_TITLE,
    PROCESS_AUDIO_BUTTON_LABEL,
    TRANSCRIPT_CARD_TITLE,
)

# Session-state key used to persist the transcript across reruns so it
# stays visible after the "Process Audio" button click completes.
_TRANSCRIPT_STATE_KEY: str = "gv_recognized_speech"


def _handle_process_audio(uploaded_file) -> None:
    """
    Runs the end-to-end Speech-to-Text flow for one uploaded audio file:
    save temporarily -> transcribe -> clean up -> store result for display.

    Args:
        uploaded_file: The Streamlit `UploadedFile` returned by the
            audio uploader widget, or None if nothing was uploaded.
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

            # Step 2: run Whisper transcription on the saved file.
            transcript = transcribe_audio(temp_audio_path)

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
    # triggered by other widgets on this page.
    st.session_state[_TRANSCRIPT_STATE_KEY] = transcript


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

        # --- Speech-to-Text: audio uploader + process button ---
        uploaded_audio = st.file_uploader(
            label=AUDIO_UPLOADER_LABEL,
            type=AUDIO_SUPPORTED_FORMATS,
            help=AUDIO_UPLOADER_HELP,
            key="gv_audio_uploader",
        )

        if st.button(PROCESS_AUDIO_BUTTON_LABEL, use_container_width=True):
            _handle_process_audio(uploaded_audio)

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

    # --- Display the recognized speech, if any, below both cards ---
    _render_transcript_if_available()

    st.write("")
    st.divider()
    placeholder_card(icon="📝", text=FILE_COMPLAINT_PLACEHOLDER)
