"""
settings.py
------------
Application settings page for GramVaani AI.

FUTURE INTEGRATION NOTE:
    This page will eventually hold language preference, notification
    preferences, and account settings, persisted via `backend/services`.
    Today it only shows the intended layout.
"""

from frontend.components.theme import page_header, placeholder_card
from frontend.config.constants import (
    SETTINGS_EYEBROW,
    SETTINGS_PLACEHOLDER,
    SETTINGS_SUBTITLE,
    SETTINGS_TITLE,
)


def render() -> None:
    """Renders the Settings page."""
    page_header(
        title=SETTINGS_TITLE,
        subtitle=SETTINGS_SUBTITLE,
        eyebrow=SETTINGS_EYEBROW,
    )

    placeholder_card(icon="⚙", text=SETTINGS_PLACEHOLDER)
