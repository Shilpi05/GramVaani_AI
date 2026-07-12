"""
constants.py
-------------
Single source of truth for all static UI text and navigation data
used across GramVaani AI.

Why this file exists:
    Pages and components should never hardcode strings like the app
    name, tagline, or sidebar labels. If those need to change, this
    is the ONLY file that should require an edit.

What does NOT live here:
    Visual/design tokens (colors, fonts, spacing) - those live in
    `frontend/components/theme.py`, since they define *appearance*
    rather than *content*. This file is content, theme.py is style.
"""

from typing import List, TypedDict


# ----------------------------------------------------------------------
# Application identity
# ----------------------------------------------------------------------
APP_NAME: str = "GramVaani AI"
APP_TAGLINE: str = "One Voice. One Platform. Better Governance."
APP_ICON: str = "🗣️"
APP_VERSION: str = "v0.1"
APP_STAGE_LABEL: str = "UI Skeleton"

SIDEBAR_BRAND_ICON: str = "🗣️"
SIDEBAR_TAGLINE: str = "Voice of the Citizen"
SIDEBAR_FOOTER: str = f"{APP_VERSION} · {APP_STAGE_LABEL}"


# ----------------------------------------------------------------------
# Navigation
# ----------------------------------------------------------------------
class NavItem(TypedDict):
    """Shape of a single sidebar navigation entry."""

    key: str
    label: str
    icon: str


NAV_ITEMS: List[NavItem] = [
    {"key": "home", "label": "Home", "icon": "🏠"},
    {"key": "file_complaint", "label": "File Complaint", "icon": "📝"},
    {"key": "scheme_finder", "label": "Scheme Finder", "icon": "🎯"},
    {"key": "track_complaint", "label": "Track Complaint", "icon": "📍"},
    {"key": "settings", "label": "Settings", "icon": "⚙"},
]

DEFAULT_PAGE: str = "home"


# ----------------------------------------------------------------------
# Home page copy
# ----------------------------------------------------------------------
HOME_EYEBROW: str = "Citizen Governance Platform"
HOME_TITLE: str = "Welcome to GramVaani AI"
HOME_SUBTITLE: str = APP_TAGLINE
HOME_DASHBOARD_PLACEHOLDER: str = "Dashboard Coming Soon"

HOME_STAT_LABELS: List[str] = [
    "Complaints Filed",
    "Schemes Matched",
    "Issues Resolved",
]


# ----------------------------------------------------------------------
# File Complaint page copy
# ----------------------------------------------------------------------
FILE_COMPLAINT_EYEBROW: str = "Grievance Redressal"
FILE_COMPLAINT_TITLE: str = "File Complaint"
FILE_COMPLAINT_SUBTITLE: str = (
    "This module will allow citizens to register complaints using voice and images."
)
FILE_COMPLAINT_VOICE_CARD_TITLE: str = "🎙 Voice Complaint"
FILE_COMPLAINT_VOICE_CARD_TEXT: str = (
    "Citizens will be able to record their complaint in their "
    "own language and have it transcribed automatically."
)
FILE_COMPLAINT_IMAGE_CARD_TITLE: str = "📷 Upload Evidence"
FILE_COMPLAINT_IMAGE_CARD_TEXT: str = (
    "Citizens will be able to attach photos of the issue "
    "(e.g. potholes, garbage, broken infrastructure)."
)
FILE_COMPLAINT_PLACEHOLDER: str = "Complaint submission workflow coming soon"

# --- Speech-to-Text feature copy (ai/speech integration) ---
AUDIO_UPLOADER_LABEL: str = "Upload your complaint audio"
AUDIO_UPLOADER_HELP: str = "Supported formats: WAV, MP3, M4A"
AUDIO_SUPPORTED_FORMATS: List[str] = ["wav", "mp3", "m4a"]

PROCESS_AUDIO_BUTTON_LABEL: str = "🎧 Process Audio"
AUDIO_PROCESSING_MESSAGE: str = "Processing your audio... please wait."

TRANSCRIPT_CARD_TITLE: str = "🗒 Recognized Speech"

AUDIO_NO_FILE_WARNING: str = "Please upload an audio file before processing."
AUDIO_EMPTY_FILE_WARNING: str = "The uploaded audio file appears to be empty."
AUDIO_UNSUPPORTED_FORMAT_ERROR: str = (
    "Unsupported file format. Please upload a WAV, MP3, or M4A file."
)
AUDIO_TRANSCRIPTION_FAILED_ERROR: str = (
    "Speech recognition failed. Please try again with a different audio file."
)
AUDIO_NO_SPEECH_DETECTED_WARNING: str = "No speech was detected in this audio file."

# --- Language selection for Speech-to-Text ---
COMPLAINT_LANGUAGE_LABEL: str = "Complaint Language"
LANGUAGE_OPTION_HINDI: str = "Hindi"
LANGUAGE_OPTION_ENGLISH: str = "English"
LANGUAGE_OPTION_AUTO: str = "Auto Detect"

# Maps the radio button label -> Whisper language code (None = auto-detect)
LANGUAGE_CODE_MAP: dict = {
    LANGUAGE_OPTION_HINDI: "hi",
    LANGUAGE_OPTION_ENGLISH: "en",
    LANGUAGE_OPTION_AUTO: None,
}
LANGUAGE_OPTIONS: List[str] = [
    LANGUAGE_OPTION_HINDI,
    LANGUAGE_OPTION_ENGLISH,
    LANGUAGE_OPTION_AUTO,
]

# --- Complaint Generation feature copy (ai/llm integration) ---
GENERATE_COMPLAINT_BUTTON_LABEL: str = "🧾 Generate Complaint"
COMPLAINT_GENERATION_PROCESSING_MESSAGE: str = "Generating your complaint... please wait."

COMPLAINT_RESULT_CARD_TITLE: str = "📋 Generated Complaint"
COMPLAINT_TYPE_LABEL: str = "Complaint Type"
COMPLAINT_DEPARTMENT_LABEL: str = "Department"
COMPLAINT_PRIORITY_LABEL: str = "Priority"
COMPLAINT_SUMMARY_LABEL: str = "Summary"
COMPLAINT_FORMAL_TEXT_LABEL: str = "Formal Complaint"

COMPLAINT_EMPTY_TRANSCRIPT_WARNING: str = (
    "There is no recognized speech yet. Please process an audio file first."
)
COMPLAINT_GENERATION_FAILED_ERROR: str = (
    "Complaint generation failed. Please try again in a moment."
)


# ----------------------------------------------------------------------
# Scheme Finder page copy
# ----------------------------------------------------------------------
SCHEME_FINDER_EYEBROW: str = "Scheme Discovery"
SCHEME_FINDER_TITLE: str = "Scheme Finder"
SCHEME_FINDER_SUBTITLE: str = "This module will recommend government schemes."
SCHEME_FINDER_CARD_TITLE: str = "🔎 How it will work"
SCHEME_FINDER_CARD_TEXT: str = (
    "Citizens will answer a few simple questions about themselves, "
    "and GramVaani AI will surface the government schemes they are "
    "most likely eligible for - in their own language."
)
SCHEME_FINDER_PLACEHOLDER: str = "Scheme recommendation engine coming soon"


# ----------------------------------------------------------------------
# Track Complaint page copy
# ----------------------------------------------------------------------
TRACK_COMPLAINT_EYEBROW: str = "Status Tracking"
TRACK_COMPLAINT_TITLE: str = "Track Complaint"
TRACK_COMPLAINT_SUBTITLE: str = "This module will allow users to track complaints."
TRACK_COMPLAINT_CARD_TITLE: str = "📍 How it will work"
TRACK_COMPLAINT_CARD_TEXT: str = (
    "Citizens will enter their complaint ID or registered phone "
    "number to see real-time status updates on their filed complaints."
)
TRACK_COMPLAINT_PLACEHOLDER: str = "Complaint tracking timeline coming soon"


# ----------------------------------------------------------------------
# Settings page copy
# ----------------------------------------------------------------------
SETTINGS_EYEBROW: str = "Preferences"
SETTINGS_TITLE: str = "Settings"
SETTINGS_SUBTITLE: str = "Application settings will appear here."
SETTINGS_PLACEHOLDER: str = "Settings panel coming soon"
