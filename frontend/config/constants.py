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
class FeatureCard(TypedDict):
    """Shape of a single entry in the Home page Features grid."""

    icon: str
    title: str
    text: str


class WorkflowStep(TypedDict):
    """Shape of a single step in the Voice Complaint Workflow strip."""

    icon: str
    title: str
    text: str


class HowItWorksStep(TypedDict):
    """Shape of a single numbered step in the How It Works section."""

    title: str
    text: str


class TrustBadge(TypedDict):
    """Shape of a single small trust-indicator pill in the hero."""

    icon: str
    label: str


HOME_EYEBROW: str = "Citizen Governance Platform"
HOME_TITLE: str = "Welcome to GramVaani AI"
HOME_SUBTITLE: str = APP_TAGLINE
HOME_DASHBOARD_PLACEHOLDER: str = "Dashboard Coming Soon"

# --- Hero section ---
HOME_HERO_EYEBROW: str = "🏛 AI-Powered Citizen Governance Platform"
HOME_HERO_HEADLINE: str = "Your Voice. Heard. Resolved."
HOME_HERO_SUBHEADLINE: str = (
    "Speak your complaint in your own language. GramVaani AI transcribes it, "
    "drafts a formal grievance, matches you with government schemes, and "
    "tracks it through to resolution - all in one place."
)
HOME_HERO_PRIMARY_CTA_LABEL: str = "🎙 File a Complaint"
HOME_HERO_PRIMARY_CTA_TARGET_PAGE: str = "file_complaint"
HOME_HERO_SECONDARY_CTA_LABEL: str = "📍 Track My Complaint"
HOME_HERO_SECONDARY_CTA_TARGET_PAGE: str = "track_complaint"

HOME_TRUST_BADGES: List[TrustBadge] = [
    {"icon": "🔐", "label": "No Login Required"},
    {"icon": "🌐", "label": "Multilingual"},
    {"icon": "🤖", "label": "AI-Powered"},
    {"icon": "📍", "label": "Real-Time Tracking"},
]

# --- Statistics section ---
# Figures are computed live from this browser session's complaint
# tracking registry (ai/utils/complaint_tracker.py) - there is no
# database, so these reset whenever the session ends. This section is
# read-only with respect to that registry; no tracking/backend logic
# is added or changed to support it.
HOME_STATS_EYEBROW: str = "This Session"
HOME_STATS_TITLE: str = "Live Activity"
HOME_STATS_SUBTITLE: str = (
    "Figures reflect complaints filed during your current browser "
    "session only - there is no database behind this platform."
)
HOME_STAT_LABELS: List[str] = [
    "Complaints Filed",
    "In Progress",
    "Resolved",
]

# --- Voice Complaint Workflow section ---
HOME_WORKFLOW_EYEBROW: str = "The Pipeline"
HOME_WORKFLOW_TITLE: str = "Voice Complaint Workflow"
HOME_WORKFLOW_SUBTITLE: str = (
    "From a spoken sentence to a filed, trackable grievance - here's "
    "what happens behind the scenes."
)
HOME_WORKFLOW_STEPS: List[WorkflowStep] = [
    {
        "icon": "🎙",
        "title": "Record or Upload",
        "text": "Speak your complaint in Hindi, English, or let the app auto-detect your language.",
    },
    {
        "icon": "📝",
        "title": "AI Transcription",
        "text": "Whisper converts your voice into accurate text within seconds.",
    },
    {
        "icon": "🤖",
        "title": "AI Drafting",
        "text": "A language model classifies, prioritizes, and drafts a formal complaint for you.",
    },
    {
        "icon": "🏛",
        "title": "Schemes + Tracking",
        "text": "Relevant government schemes are matched, and a Complaint ID is issued for tracking.",
    },
]

# --- Features section ---
HOME_FEATURES_EYEBROW: str = "Capabilities"
HOME_FEATURES_TITLE: str = "Everything a Citizen Needs"
HOME_FEATURES_SUBTITLE: str = (
    "A complete, self-service grievance pipeline - no forms, no queues, no login."
)
HOME_FEATURES: List[FeatureCard] = [
    {
        "icon": "🎙",
        "title": "Voice-to-Text",
        "text": "Speak naturally in your own language - Whisper transcribes it instantly and accurately.",
    },
    {
        "icon": "🤖",
        "title": "AI Complaint Drafting",
        "text": "An LLM turns your words into a formal, department-ready complaint in seconds.",
    },
    {
        "icon": "🏛",
        "title": "Scheme Recommendations",
        "text": "Automatically matched with relevant government welfare schemes based on your complaint.",
    },
    {
        "icon": "📄",
        "title": "PDF Export",
        "text": "Download a professionally formatted PDF copy of your complaint for your own records.",
    },
    {
        "icon": "📍",
        "title": "Status Tracking",
        "text": "Follow your complaint's journey from Submitted to Resolved using a unique Complaint ID.",
    },
    {
        "icon": "🔐",
        "title": "Privacy First",
        "text": "No account, no login. Your data stays within your session - nothing is stored beyond it.",
    },
]

# --- How It Works section ---
HOME_HOW_IT_WORKS_EYEBROW: str = "For Citizens"
HOME_HOW_IT_WORKS_TITLE: str = "How It Works"
HOME_HOW_IT_WORKS_SUBTITLE: str = "Three simple steps - no paperwork, no waiting in line."
HOME_HOW_IT_WORKS_STEPS: List[HowItWorksStep] = [
    {
        "title": "Speak Your Complaint",
        "text": "Upload or record a short voice note describing the issue, in your own language.",
    },
    {
        "title": "Let AI Do the Paperwork",
        "text": "GramVaani AI transcribes, classifies, and drafts a formal complaint automatically.",
    },
    {
        "title": "Track Until Resolved",
        "text": "Use your Complaint ID anytime to check status - Submitted, Under Review, Assigned, Resolved.",
    },
]

# --- Closing CTA banner ---
HOME_CTA_BANNER_TITLE: str = "Ready to raise your voice?"
HOME_CTA_BANNER_SUBTITLE: str = "It takes less than a minute to file your first complaint."
HOME_CTA_BANNER_BUTTON_LABEL: str = "🎙 Get Started"
HOME_CTA_BANNER_TARGET_PAGE: str = "file_complaint"


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
COMPLAINT_ID_LABEL: str = "Complaint ID"
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

# --- Government Scheme Recommendation feature copy (ai/schemes integration) ---
SCHEME_RECOMMENDATION_CARD_TITLE: str = "🏛 Recommended Government Schemes"
SCHEME_NAME_LABEL: str = "Scheme Name"
SCHEME_DESCRIPTION_LABEL: str = "Description"
SCHEME_ELIGIBILITY_LABEL: str = "Eligibility"
SCHEME_DEPARTMENT_LABEL: str = "Responsible Department"
SCHEME_NO_MATCH_MESSAGE: str = "No direct government scheme found."

# --- PDF Export feature copy (ai/utils/pdf_generator integration) ---
DOWNLOAD_COMPLAINT_BUTTON_LABEL: str = "📄 Download Complaint"
PDF_GENERATION_FAILED_ERROR: str = (
    "Could not generate the PDF for this complaint. Please try again."
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
TRACK_COMPLAINT_SUBTITLE: str = (
    "Enter your Complaint ID to check its current status."
)
TRACK_COMPLAINT_CARD_TITLE: str = "📍 How it works"
TRACK_COMPLAINT_CARD_TEXT: str = (
    "Enter the Complaint ID shown when your complaint was generated "
    "(e.g. GV-20260713-00001) to see its current status. This is a "
    "mock tracker - complaint status is simulated locally for this "
    "browser session only and is not stored in any database."
)

TRACK_COMPLAINT_ID_INPUT_LABEL: str = "Complaint ID"
TRACK_COMPLAINT_ID_INPUT_PLACEHOLDER: str = "e.g. GV-20260713-00001"
TRACK_COMPLAINT_BUTTON_LABEL: str = "🔍 Track Complaint"

TRACK_COMPLAINT_EMPTY_ID_WARNING: str = "Please enter a Complaint ID to track."
TRACK_COMPLAINT_NOT_FOUND_WARNING: str = (
    "No complaint found with this ID in the current session. "
    "Complaint tracking only works for complaints generated during "
    "this browser session - it resets if the app restarts or the "
    "session ends."
)

TRACK_COMPLAINT_RESULT_CARD_TITLE: str = "📦 Complaint Status"
TRACK_COMPLAINT_STATUS_LABEL: str = "Status"
TRACK_COMPLAINT_DEPARTMENT_LABEL: str = "Department"
TRACK_COMPLAINT_DATE_LABEL: str = "Date"
TRACK_COMPLAINT_PRIORITY_LABEL: str = "Priority"

TRACK_COMPLAINT_PLACEHOLDER: str = "Complaint tracking timeline coming soon"


# ----------------------------------------------------------------------
# Settings page copy
# ----------------------------------------------------------------------
SETTINGS_EYEBROW: str = "Preferences"
SETTINGS_TITLE: str = "Settings"
SETTINGS_SUBTITLE: str = "Application settings will appear here."
SETTINGS_PLACEHOLDER: str = "Settings panel coming soon"