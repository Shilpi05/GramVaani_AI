"""
track_complaint.py
--------------------
Complaint tracking page for GramVaani AI.

FUTURE INTEGRATION NOTE:
    This page will eventually query `backend/services` for a complaint's
    status by ID or citizen phone number, and display a timeline
    (Filed -> In Review -> Resolved). No data wiring exists yet.
"""

import streamlit as st

from frontend.components.theme import page_header, placeholder_card
from frontend.config.constants import (
    TRACK_COMPLAINT_CARD_TEXT,
    TRACK_COMPLAINT_CARD_TITLE,
    TRACK_COMPLAINT_EYEBROW,
    TRACK_COMPLAINT_PLACEHOLDER,
    TRACK_COMPLAINT_SUBTITLE,
    TRACK_COMPLAINT_TITLE,
)


def render() -> None:
    """Renders the Track Complaint page."""
    page_header(
        title=TRACK_COMPLAINT_TITLE,
        subtitle=TRACK_COMPLAINT_SUBTITLE,
        eyebrow=TRACK_COMPLAINT_EYEBROW,
    )

    st.markdown(
        f"""
        <div class="gv-card">
            <h3>{TRACK_COMPLAINT_CARD_TITLE}</h3>
            <p>{TRACK_COMPLAINT_CARD_TEXT}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.divider()
    placeholder_card(icon="📦", text=TRACK_COMPLAINT_PLACEHOLDER)
