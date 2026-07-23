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
# Populated so far: navigation (sidebar nav labels, the app title, and
# the tagline - see `frontend/components/sidebar.py`) and every page
# under `frontend/pages/`: Home, File Complaint, Scheme Finder, Track
# Complaint, and Settings.
#
# Note on structured "home.*"/"file_complaint.*" keys: several (e.g.
# "home.features.items", "file_complaint.language_option_labels") map
# to a list/dict rather than a plain string. Icons (emoji) inside list-
# of-dict values are identical across languages and kept only for
# convenience of co-locating them with their translated title/text -
# they are not translated content themselves. Similarly, the keys of
# "file_complaint.language_option_labels" are the canonical English
# option values from `frontend/config/constants.py` (LANGUAGE_OPTIONS)
# - shared, unchanging session-state values - only their dict values
# (the on-screen label) vary by language.
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

        # ---------- Home page: Hero ----------
        "home.hero.eyebrow": "🏛 AI-Powered Citizen Governance Platform",
        "home.hero.headline": "Your Voice. Heard. Resolved.",
        "home.hero.subheadline": (
            "Speak your complaint in your own language. GramVaani AI "
            "transcribes it, drafts a formal grievance, matches you with "
            "government schemes, and tracks it through to resolution - "
            "all in one place."
        ),
        "home.hero.primary_cta_label": "🎙 File a Complaint",
        "home.hero.secondary_cta_label": "📍 Track My Complaint",
        "home.hero.trust_badges": [
            {"icon": "🔐", "label": "No Login Required"},
            {"icon": "🌐", "label": "Multilingual"},
            {"icon": "🤖", "label": "AI-Powered"},
            {"icon": "📍", "label": "Real-Time Tracking"},
        ],

        # ---------- Home page: Statistics ----------
        "home.stats.eyebrow": "This Session",
        "home.stats.title": "Live Activity",
        "home.stats.subtitle": (
            "Figures reflect complaints filed during your current browser "
            "session only - there is no database behind this platform."
        ),
        "home.stats.labels": ["Complaints Filed", "In Progress", "Resolved"],

        # ---------- Home page: Voice Complaint Workflow ----------
        "home.workflow.eyebrow": "The Pipeline",
        "home.workflow.title": "Voice Complaint Workflow",
        "home.workflow.subtitle": (
            "From a spoken sentence to a filed, trackable grievance - "
            "here's what happens behind the scenes."
        ),
        "home.workflow.step_label": "Step",
        "home.workflow.steps": [
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
        ],

        # ---------- Home page: Features ----------
        "home.features.eyebrow": "Capabilities",
        "home.features.title": "Everything a Citizen Needs",
        "home.features.subtitle": (
            "A complete, self-service grievance pipeline - no forms, no queues, no login."
        ),
        "home.features.items": [
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
        ],

        # ---------- Home page: How It Works ----------
        "home.how_it_works.eyebrow": "For Citizens",
        "home.how_it_works.title": "How It Works",
        "home.how_it_works.subtitle": "Three simple steps - no paperwork, no waiting in line.",
        "home.how_it_works.steps": [
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
        ],

        # ---------- Home page: Closing CTA banner ----------
        "home.cta_banner.title": "Ready to raise your voice?",
        "home.cta_banner.subtitle": "It takes less than a minute to file your first complaint.",
        "home.cta_banner.button_label": "🎙 Get Started",

        # ---------- File Complaint page ----------
        "file_complaint.eyebrow": "Grievance Redressal",
        "file_complaint.title": "File Complaint",
        "file_complaint.subtitle": (
            "Register a complaint using your voice, with an optional evidence photo."
        ),
        "file_complaint.voice_card_title": "🎙 Voice Complaint",
        "file_complaint.voice_card_text": (
            "Record your complaint in your own language and it will be "
            "transcribed automatically."
        ),
        "file_complaint.image_card_title": "📷 Upload Evidence",
        "file_complaint.image_card_text": (
            "Optionally attach a photo of the issue (e.g. potholes, garbage, "
            "broken infrastructure) to support your complaint."
        ),
        "file_complaint.evidence_attached_note": "📎 Evidence photo attached:",

        "file_complaint.audio_uploader_label": "Upload your complaint audio",
        "file_complaint.audio_uploader_help": "Supported formats: WAV, MP3, M4A",
        "file_complaint.process_audio_button_label": "🎧 Process Audio",
        "file_complaint.audio_processing_message": "Processing your audio... please wait.",
        "file_complaint.transcript_card_title": "🗒 Recognized Speech",
        "file_complaint.audio_no_file_warning": "Please upload an audio file before processing.",
        "file_complaint.audio_empty_file_warning": "The uploaded audio file appears to be empty.",
        "file_complaint.audio_unsupported_format_error": (
            "Unsupported file format. Please upload a WAV, MP3, or M4A file."
        ),
        "file_complaint.audio_transcription_failed_error": (
            "Speech recognition failed. Please try again with a different audio file."
        ),
        "file_complaint.audio_no_speech_detected_warning": "No speech was detected in this audio file.",

        "file_complaint.language_label": "Complaint Language",
        # Keys here are the canonical option values in
        # `frontend/config/constants.py` (LANGUAGE_OPTIONS) - the values
        # actually stored in `st.session_state["gv_complaint_language"]`
        # and shared with `frontend/pages/settings.py`. Only the
        # DISPLAYED label (used via `format_func`) is translated; the
        # underlying stored value never changes with language, so the
        # setting stays valid across both pages regardless of the
        # active interface language.
        "file_complaint.language_option_labels": {
            "Hindi": "Hindi",
            "English": "English",
            "Auto Detect": "Auto Detect",
        },

        "file_complaint.generate_complaint_button_label": "🧾 Generate Complaint",
        "file_complaint.generation_processing_message": "Generating your complaint... please wait.",

        "file_complaint.result_card_title": "📋 Generated Complaint",
        "file_complaint.complaint_id_label": "Complaint ID",
        "file_complaint.complaint_type_label": "Complaint Type",
        "file_complaint.department_label": "Department",
        "file_complaint.priority_label": "Priority",
        "file_complaint.summary_label": "Summary",
        "file_complaint.formal_text_label": "Formal Complaint",

        "file_complaint.empty_transcript_warning": (
            "There is no recognized speech yet. Please process an audio file first."
        ),
        "file_complaint.scheme_no_match_message": "No direct government scheme found.",

        "file_complaint.download_button_label": "📄 Download Complaint",
        "file_complaint.pdf_generation_failed_error": (
            "Could not generate the PDF for this complaint. Please try again."
        ),

        # ---------- Scheme Finder page ----------
        "scheme_finder.eyebrow": "Scheme Discovery",
        "scheme_finder.title": "Scheme Finder",
        "scheme_finder.subtitle": (
            "Government schemes relevant to your complaint, matched automatically."
        ),
        "scheme_finder.card_title": "🔎 How it works",
        "scheme_finder.card_text": (
            "When you file a complaint, GramVaani AI matches its type, "
            "department, and summary against a local knowledge base of "
            "government schemes. Anything relevant appears below - no extra "
            "steps needed."
        ),
        "scheme_finder.recommendation_card_title": "🏛 Recommended Government Schemes",
        "scheme_finder.eligibility_label": "Eligibility",
        "scheme_finder.department_label": "Responsible Department",
        "scheme_finder.empty_state_text": (
            "No schemes to show yet - file a complaint first and any relevant "
            "government schemes will appear here automatically."
        ),
        "scheme_finder.empty_state_button_label": "📝 File a Complaint",

        # ---------- Track Complaint page ----------
        "track_complaint.eyebrow": "Status Tracking",
        "track_complaint.title": "Track Complaint",
        "track_complaint.subtitle": "Enter your Complaint ID to check its current status.",
        "track_complaint.card_title": "📍 How it works",
        "track_complaint.card_text": (
            "Enter the Complaint ID shown when your complaint was generated "
            "(e.g. GV-20260713-00001) to see its current status. This is a "
            "mock tracker - complaint status is simulated locally for this "
            "browser session only and is not stored in any database."
        ),
        "track_complaint.id_input_label": "Complaint ID",
        "track_complaint.id_input_placeholder": "e.g. GV-20260713-00001",
        "track_complaint.button_label": "🔍 Track Complaint",

        "track_complaint.empty_id_warning": "Please enter a Complaint ID to track.",
        "track_complaint.not_found_warning": (
            "No complaint found with this ID in the current session. "
            "Complaint tracking only works for complaints generated during "
            "this browser session - it resets if the app restarts or the "
            "session ends."
        ),

        "track_complaint.result_card_title": "📦 Complaint Status",
        "track_complaint.complaint_id_label": "Complaint ID",
        "track_complaint.status_label": "Current Status",
        "track_complaint.department_label": "Department",
        "track_complaint.date_label": "Submission Date",
        "track_complaint.priority_label": "Priority",
        "track_complaint.estimated_resolution_label": "Estimated Resolution Time",
        "track_complaint.last_updated_label": "Last Updated",
        "track_complaint.resolved_confirmation_prefix": "Verified as resolved on",

        "track_complaint.not_found_title": "Complaint Not Found",
        "track_complaint.empty_id_title": "Enter a Complaint ID",

        "track_complaint.timeline_card_title": "🕒 Complaint Timeline",
        "track_complaint.current_stage_tag": "Current Stage",
        # Positionally matches the internal DISPLAY_STAGES list in
        # `frontend/pages/track_complaint.py` - those English values
        # remain the canonical lookup keys for the (untranslated,
        # per-instructions) officer remarks; this list only supplies
        # the translated on-screen timeline heading for each stage.
        "track_complaint.display_stage_labels": [
            "Complaint Submitted",
            "Under Review",
            "Assigned to Municipal Officer",
            "Officer Visit Scheduled",
            "Resolved",
        ],

        "track_complaint.remarks_card_title": "🗒️ Officer Remarks",

        "track_complaint.contact_card_title": "🏢 Department Contact",
        "track_complaint.contact_department_label": "Responsible Department",
        "track_complaint.contact_officer_label": "Officer",
        "track_complaint.contact_phone_label": "Phone",
        "track_complaint.contact_email_label": "Email",
        "track_complaint.contact_mock_note": (
            "This is mock contact information for demo purposes and does not "
            "represent a real government office."
        ),

        # ---------- Settings page ----------
        "settings.eyebrow": "Preferences",
        "settings.title": "Settings",
        "settings.subtitle": "Manage your preferences and session data.",

        "settings.app_info_title": "Application Status",
        "settings.app_name_label": "Application",
        "settings.version_label": "Version",
        "settings.ai_assistance_label": "AI Assistance",
        "settings.ai_assistance_value": "Enabled",
        "settings.speech_recognition_label": "Speech Recognition",
        "settings.speech_recognition_value": "Available",

        "settings.preferences_title": "Preferences",
        "settings.app_language_label": "Application Language",
        "settings.app_language_help": (
            "Changes the language of the app's own interface - menus, labels, and messages."
        ),
        "settings.language_label": "Preferred Complaint Language",
        "settings.language_help": (
            "Sets the default selection on the File Complaint page's "
            "language chooser. Ignored while Auto Detect is on."
        ),
        "settings.auto_delete_label": "Auto Delete Uploaded Files",
        "settings.auto_delete_help": (
            "When on, a previous evidence photo is deleted from disk as soon "
            "as it's replaced with a new one."
        ),

        "settings.system_title": "System",
        "settings.clear_session_button_label": "🗑 Clear Session",
        "settings.clear_session_help": (
            "Clears this session's transcript, generated complaint, scheme "
            "results, evidence photo, and tracking records. Preferences below "
            "are not affected."
        ),
        "settings.clear_session_success_message": "Session data cleared.",
        "settings.restore_defaults_button_label": "↺ Restore Defaults",
        "settings.restore_defaults_help": (
            "Resets Preferred Language, Auto Detect, and Auto Delete above "
            "back to their original defaults."
        ),
        "settings.restore_defaults_success_message": "Preferences restored to defaults.",
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

        # ---------- Home page: Hero ----------
        "home.hero.eyebrow": "🏛 एआई-संचालित नागरिक शासन मंच",
        "home.hero.headline": "आपकी आवाज़। सुनी गई। सुलझाई गई।",
        "home.hero.subheadline": (
            "अपनी शिकायत अपनी भाषा में बोलें। ग्रामवाणी एआई इसे लिखित रूप "
            "देता है, एक औपचारिक शिकायत तैयार करता है, आपको सरकारी योजनाओं "
            "से जोड़ता है, और समाधान तक इसे ट्रैक करता है - सब कुछ एक ही जगह।"
        ),
        "home.hero.primary_cta_label": "🎙 शिकायत दर्ज करें",
        "home.hero.secondary_cta_label": "📍 मेरी शिकायत ट्रैक करें",
        "home.hero.trust_badges": [
            {"icon": "🔐", "label": "लॉगिन की आवश्यकता नहीं"},
            {"icon": "🌐", "label": "बहुभाषी"},
            {"icon": "🤖", "label": "एआई-संचालित"},
            {"icon": "📍", "label": "रीयल-टाइम ट्रैकिंग"},
        ],

        # ---------- Home page: Statistics ----------
        "home.stats.eyebrow": "इस सत्र में",
        "home.stats.title": "लाइव गतिविधि",
        "home.stats.subtitle": (
            "आंकड़े केवल आपके वर्तमान ब्राउज़र सत्र के दौरान दर्ज की गई "
            "शिकायतों को दर्शाते हैं - इस मंच के पीछे कोई डेटाबेस नहीं है।"
        ),
        "home.stats.labels": ["दर्ज शिकायतें", "प्रगति में", "सुलझाई गई"],

        # ---------- Home page: Voice Complaint Workflow ----------
        "home.workflow.eyebrow": "प्रक्रिया",
        "home.workflow.title": "वॉइस शिकायत वर्कफ़्लो",
        "home.workflow.subtitle": (
            "बोले गए वाक्य से लेकर दर्ज, ट्रैक करने योग्य शिकायत तक - "
            "पर्दे के पीछे यही होता है।"
        ),
        "home.workflow.step_label": "चरण",
        "home.workflow.steps": [
            {
                "icon": "🎙",
                "title": "रिकॉर्ड करें या अपलोड करें",
                "text": "हिंदी या अंग्रेज़ी में अपनी शिकायत बोलें, या ऐप को अपनी भाषा स्वतः पहचानने दें।",
            },
            {
                "icon": "📝",
                "title": "एआई ट्रांसक्रिप्शन",
                "text": "व्हिस्पर कुछ ही सेकंड में आपकी आवाज़ को सटीक टेक्स्ट में बदल देता है।",
            },
            {
                "icon": "🤖",
                "title": "एआई ड्राफ्टिंग",
                "text": "एक भाषा मॉडल आपके लिए शिकायत को वर्गीकृत करता है, प्राथमिकता तय करता है, और एक औपचारिक शिकायत तैयार करता है।",
            },
            {
                "icon": "🏛",
                "title": "योजनाएं + ट्रैकिंग",
                "text": "संबंधित सरकारी योजनाओं का मिलान किया जाता है, और ट्रैकिंग के लिए एक शिकायत आईडी जारी की जाती है।",
            },
        ],

        # ---------- Home page: Features ----------
        "home.features.eyebrow": "क्षमताएं",
        "home.features.title": "एक नागरिक की हर ज़रूरत",
        "home.features.subtitle": (
            "एक पूर्ण, स्व-सेवा शिकायत प्रक्रिया - कोई फॉर्म नहीं, कोई कतार नहीं, कोई लॉगिन नहीं।"
        ),
        "home.features.items": [
            {
                "icon": "🎙",
                "title": "वॉइस-टू-टेक्स्ट",
                "text": "अपनी भाषा में स्वाभाविक रूप से बोलें - व्हिस्पर इसे तुरंत और सटीक रूप से लिख देता है।",
            },
            {
                "icon": "🤖",
                "title": "एआई शिकायत ड्राफ्टिंग",
                "text": "एक एलएलएम कुछ ही सेकंड में आपके शब्दों को एक औपचारिक, विभाग के लिए तैयार शिकायत में बदल देता है।",
            },
            {
                "icon": "🏛",
                "title": "योजना अनुशंसाएं",
                "text": "आपकी शिकायत के आधार पर संबंधित सरकारी कल्याण योजनाओं से स्वतः मिलान किया जाता है।",
            },
            {
                "icon": "📄",
                "title": "पीडीएफ एक्सपोर्ट",
                "text": "अपने रिकॉर्ड के लिए अपनी शिकायत की एक पेशेवर रूप से स्वरूपित पीडीएफ प्रति डाउनलोड करें।",
            },
            {
                "icon": "📍",
                "title": "स्थिति ट्रैकिंग",
                "text": "एक अद्वितीय शिकायत आईडी का उपयोग करके अपनी शिकायत की यात्रा को सबमिट किए जाने से लेकर सुलझाए जाने तक फॉलो करें।",
            },
            {
                "icon": "🔐",
                "title": "गोपनीयता सर्वोपरि",
                "text": "कोई खाता नहीं, कोई लॉगिन नहीं। आपका डेटा आपके सत्र के भीतर ही रहता है - इसके आगे कुछ भी संग्रहीत नहीं होता।",
            },
        ],

        # ---------- Home page: How It Works ----------
        "home.how_it_works.eyebrow": "नागरिकों के लिए",
        "home.how_it_works.title": "यह कैसे काम करता है",
        "home.how_it_works.subtitle": "तीन आसान चरण - कोई कागज़ी कार्रवाई नहीं, कतार में इंतज़ार नहीं।",
        "home.how_it_works.steps": [
            {
                "title": "अपनी शिकायत बोलें",
                "text": "समस्या का वर्णन करते हुए अपनी भाषा में एक छोटा वॉइस नोट अपलोड करें या रिकॉर्ड करें।",
            },
            {
                "title": "कागज़ी कार्रवाई एआई पर छोड़ें",
                "text": "ग्रामवाणी एआई स्वचालित रूप से लिखित रूप देता है, वर्गीकृत करता है, और एक औपचारिक शिकायत तैयार करता है।",
            },
            {
                "title": "समाधान तक ट्रैक करें",
                "text": "स्थिति जांचने के लिए कभी भी अपनी शिकायत आईडी का उपयोग करें - सबमिट की गई, समीक्षाधीन, नियत, सुलझाई गई।",
            },
        ],

        # ---------- Home page: Closing CTA banner ----------
        "home.cta_banner.title": "अपनी आवाज़ उठाने के लिए तैयार हैं?",
        "home.cta_banner.subtitle": "अपनी पहली शिकायत दर्ज करने में एक मिनट से भी कम समय लगता है।",
        "home.cta_banner.button_label": "🎙 शुरू करें",

        # ---------- File Complaint page ----------
        "file_complaint.eyebrow": "शिकायत निवारण",
        "file_complaint.title": "शिकायत दर्ज करें",
        "file_complaint.subtitle": (
            "अपनी आवाज़ का उपयोग करके शिकायत दर्ज करें, वैकल्पिक साक्ष्य फोटो के साथ।"
        ),
        "file_complaint.voice_card_title": "🎙 वॉइस शिकायत",
        "file_complaint.voice_card_text": (
            "अपनी भाषा में अपनी शिकायत रिकॉर्ड करें और यह स्वचालित रूप से "
            "लिखित रूप में बदल जाएगी।"
        ),
        "file_complaint.image_card_title": "📷 साक्ष्य अपलोड करें",
        "file_complaint.image_card_text": (
            "अपनी शिकायत के समर्थन में समस्या (जैसे गड्ढे, कचरा, क्षतिग्रस्त "
            "बुनियादी ढांचा) की एक तस्वीर वैकल्पिक रूप से संलग्न करें।"
        ),
        "file_complaint.evidence_attached_note": "📎 साक्ष्य फोटो संलग्न:",

        "file_complaint.audio_uploader_label": "अपनी शिकायत का ऑडियो अपलोड करें",
        "file_complaint.audio_uploader_help": "समर्थित प्रारूप: WAV, MP3, M4A",
        "file_complaint.process_audio_button_label": "🎧 ऑडियो प्रोसेस करें",
        "file_complaint.audio_processing_message": "आपका ऑडियो प्रोसेस किया जा रहा है... कृपया प्रतीक्षा करें।",
        "file_complaint.transcript_card_title": "🗒 पहचानी गई वाणी",
        "file_complaint.audio_no_file_warning": "प्रोसेस करने से पहले कृपया एक ऑडियो फ़ाइल अपलोड करें।",
        "file_complaint.audio_empty_file_warning": "अपलोड की गई ऑडियो फ़ाइल खाली प्रतीत होती है।",
        "file_complaint.audio_unsupported_format_error": (
            "असमर्थित फ़ाइल प्रारूप। कृपया WAV, MP3, या M4A फ़ाइल अपलोड करें।"
        ),
        "file_complaint.audio_transcription_failed_error": (
            "वाणी पहचान विफल हुई। कृपया किसी भिन्न ऑडियो फ़ाइल के साथ पुनः प्रयास करें।"
        ),
        "file_complaint.audio_no_speech_detected_warning": "इस ऑडियो फ़ाइल में कोई वाणी नहीं मिली।",

        "file_complaint.language_label": "शिकायत की भाषा",
        "file_complaint.language_option_labels": {
            "Hindi": "हिंदी",
            "English": "अंग्रेज़ी",
            "Auto Detect": "स्वतः पहचानें",
        },

        "file_complaint.generate_complaint_button_label": "🧾 शिकायत तैयार करें",
        "file_complaint.generation_processing_message": "आपकी शिकायत तैयार की जा रही है... कृपया प्रतीक्षा करें।",

        "file_complaint.result_card_title": "📋 तैयार की गई शिकायत",
        "file_complaint.complaint_id_label": "शिकायत आईडी",
        "file_complaint.complaint_type_label": "शिकायत प्रकार",
        "file_complaint.department_label": "विभाग",
        "file_complaint.priority_label": "प्राथमिकता",
        "file_complaint.summary_label": "सारांश",
        "file_complaint.formal_text_label": "औपचारिक शिकायत",

        "file_complaint.empty_transcript_warning": (
            "अभी तक कोई पहचानी गई वाणी नहीं है। कृपया पहले एक ऑडियो फ़ाइल प्रोसेस करें।"
        ),
        "file_complaint.scheme_no_match_message": "कोई सीधी सरकारी योजना नहीं मिली।",

        "file_complaint.download_button_label": "📄 शिकायत डाउनलोड करें",
        "file_complaint.pdf_generation_failed_error": (
            "इस शिकायत के लिए पीडीएफ जनरेट नहीं किया जा सका। कृपया पुनः प्रयास करें।"
        ),

        # ---------- Scheme Finder page ----------
        "scheme_finder.eyebrow": "योजना खोज",
        "scheme_finder.title": "योजना खोजक",
        "scheme_finder.subtitle": (
            "आपकी शिकायत से संबंधित सरकारी योजनाएं, स्वचालित रूप से मिलान की गई।"
        ),
        "scheme_finder.card_title": "🔎 यह कैसे काम करता है",
        "scheme_finder.card_text": (
            "जब आप शिकायत दर्ज करते हैं, तो ग्रामवाणी एआई इसके प्रकार, विभाग "
            "और सारांश का सरकारी योजनाओं के स्थानीय ज्ञान आधार से मिलान करता "
            "है। जो भी प्रासंगिक हो वह नीचे दिखाई देता है - किसी अतिरिक्त "
            "चरण की आवश्यकता नहीं।"
        ),
        "scheme_finder.recommendation_card_title": "🏛 अनुशंसित सरकारी योजनाएं",
        "scheme_finder.eligibility_label": "पात्रता",
        "scheme_finder.department_label": "जिम्मेदार विभाग",
        "scheme_finder.empty_state_text": (
            "अभी दिखाने के लिए कोई योजना नहीं है - पहले एक शिकायत दर्ज करें "
            "और कोई भी प्रासंगिक सरकारी योजना यहां स्वचालित रूप से दिखाई देगी।"
        ),
        "scheme_finder.empty_state_button_label": "📝 शिकायत दर्ज करें",

        # ---------- Track Complaint page ----------
        "track_complaint.eyebrow": "स्थिति ट्रैकिंग",
        "track_complaint.title": "शिकायत ट्रैक करें",
        "track_complaint.subtitle": "अपनी शिकायत की वर्तमान स्थिति जांचने के लिए अपनी शिकायत आईडी दर्ज करें।",
        "track_complaint.card_title": "📍 यह कैसे काम करता है",
        "track_complaint.card_text": (
            "अपनी शिकायत की वर्तमान स्थिति देखने के लिए शिकायत जनरेट होने पर "
            "दिखाई गई शिकायत आईडी (जैसे GV-20260713-00001) दर्ज करें। यह एक "
            "मॉक ट्रैकर है - शिकायत की स्थिति केवल इस ब्राउज़र सत्र के लिए "
            "स्थानीय रूप से सिम्युलेट की जाती है और किसी डेटाबेस में संग्रहीत "
            "नहीं है।"
        ),
        "track_complaint.id_input_label": "शिकायत आईडी",
        "track_complaint.id_input_placeholder": "उदा. GV-20260713-00001",
        "track_complaint.button_label": "🔍 शिकायत ट्रैक करें",

        "track_complaint.empty_id_warning": "ट्रैक करने के लिए कृपया एक शिकायत आईडी दर्ज करें।",
        "track_complaint.not_found_warning": (
            "वर्तमान सत्र में इस आईडी के साथ कोई शिकायत नहीं मिली। शिकायत "
            "ट्रैकिंग केवल इस ब्राउज़र सत्र के दौरान दर्ज की गई शिकायतों के "
            "लिए काम करती है - ऐप पुनः आरंभ होने या सत्र समाप्त होने पर यह "
            "रीसेट हो जाती है।"
        ),

        "track_complaint.result_card_title": "📦 शिकायत की स्थिति",
        "track_complaint.complaint_id_label": "शिकायत आईडी",
        "track_complaint.status_label": "वर्तमान स्थिति",
        "track_complaint.department_label": "विभाग",
        "track_complaint.date_label": "दर्ज करने की तिथि",
        "track_complaint.priority_label": "प्राथमिकता",
        "track_complaint.estimated_resolution_label": "अनुमानित समाधान समय",
        "track_complaint.last_updated_label": "अंतिम अद्यतन",
        "track_complaint.resolved_confirmation_prefix": "इस तारीख को सुलझाई गई के रूप में सत्यापित",

        "track_complaint.not_found_title": "शिकायत नहीं मिली",
        "track_complaint.empty_id_title": "एक शिकायत आईडी दर्ज करें",

        "track_complaint.timeline_card_title": "🕒 शिकायत समयरेखा",
        "track_complaint.current_stage_tag": "वर्तमान चरण",
        "track_complaint.display_stage_labels": [
            "शिकायत दर्ज की गई",
            "समीक्षाधीन",
            "नगरपालिका अधिकारी को सौंपी गई",
            "अधिकारी का दौरा निर्धारित",
            "सुलझाई गई",
        ],

        "track_complaint.remarks_card_title": "🗒️ अधिकारी की टिप्पणियां",

        "track_complaint.contact_card_title": "🏢 विभाग संपर्क",
        "track_complaint.contact_department_label": "जिम्मेदार विभाग",
        "track_complaint.contact_officer_label": "अधिकारी",
        "track_complaint.contact_phone_label": "फ़ोन",
        "track_complaint.contact_email_label": "ईमेल",
        "track_complaint.contact_mock_note": (
            "यह डेमो उद्देश्यों के लिए मॉक संपर्क जानकारी है और किसी वास्तविक "
            "सरकारी कार्यालय का प्रतिनिधित्व नहीं करती।"
        ),

        # ---------- Settings page ----------
        "settings.eyebrow": "प्राथमिकताएं",
        "settings.title": "सेटिंग्स",
        "settings.subtitle": "अपनी प्राथमिकताओं और सत्र डेटा को प्रबंधित करें।",

        "settings.app_info_title": "एप्लिकेशन स्थिति",
        "settings.app_name_label": "एप्लिकेशन",
        "settings.version_label": "संस्करण",
        "settings.ai_assistance_label": "एआई सहायता",
        "settings.ai_assistance_value": "सक्षम",
        "settings.speech_recognition_label": "वाणी पहचान",
        "settings.speech_recognition_value": "उपलब्ध",

        "settings.preferences_title": "प्राथमिकताएं",
        "settings.app_language_label": "एप्लिकेशन भाषा",
        "settings.app_language_help": (
            "ऐप के अपने इंटरफ़ेस की भाषा बदलता है - मेनू, लेबल और संदेश।"
        ),
        "settings.language_label": "पसंदीदा शिकायत भाषा",
        "settings.language_help": (
            "फ़ाइल शिकायत पृष्ठ के भाषा चयनकर्ता पर डिफ़ॉल्ट चयन सेट करता है। "
            "जब स्वतः पहचान चालू हो तो इसे नज़रअंदाज़ किया जाता है।"
        ),
        "settings.auto_delete_label": "अपलोड की गई फ़ाइलें स्वतः हटाएं",
        "settings.auto_delete_help": (
            "चालू होने पर, पिछली साक्ष्य फोटो को नई फोटो से बदलते ही डिस्क "
            "से हटा दिया जाता है।"
        ),

        "settings.system_title": "सिस्टम",
        "settings.clear_session_button_label": "🗑 सत्र साफ़ करें",
        "settings.clear_session_help": (
            "इस सत्र की ट्रांसक्रिप्ट, तैयार की गई शिकायत, योजना परिणाम, "
            "साक्ष्य फोटो, और ट्रैकिंग रिकॉर्ड साफ़ करता है। नीचे दी गई "
            "प्राथमिकताएं प्रभावित नहीं होतीं।"
        ),
        "settings.clear_session_success_message": "सत्र डेटा साफ़ किया गया।",
        "settings.restore_defaults_button_label": "↺ डिफ़ॉल्ट पुनर्स्थापित करें",
        "settings.restore_defaults_help": (
            "ऊपर दी गई पसंदीदा भाषा, स्वतः पहचान, और स्वतः हटाएं को उनके "
            "मूल डिफ़ॉल्ट पर पुनर्स्थापित करता है।"
        ),
        "settings.restore_defaults_success_message": "प्राथमिकताएं डिफ़ॉल्ट पर पुनर्स्थापित की गईं।",
    },
}