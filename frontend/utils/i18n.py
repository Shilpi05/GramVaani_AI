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
# the tagline - see `frontend/components/sidebar.py`) and the Home page
# (`frontend/pages/home.py`). Other page content (File Complaint,
# Scheme Finder, Track Complaint, Settings) is still entirely in
# English and untouched by this module; that's a later pass, not an
# oversight.
#
# Note on structured "home.*" keys: several (e.g. "home.features.items",
# "home.workflow.steps") map to a list of dicts rather than a plain
# string. Icons (emoji) inside those dicts are identical across
# languages and kept only for convenience of co-locating them with
# their translated title/text - they are not translated content
# themselves.
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
    },
}