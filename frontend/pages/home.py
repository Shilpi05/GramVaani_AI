"""
home.py
--------
Home / landing page for GramVaani AI.

FUTURE INTEGRATION NOTE:
    The "Dashboard Coming Soon" card below is where live stats will
    eventually render - e.g. total complaints filed, resolution rate,
    active schemes. That data will come from `backend/` once it exists.
    For now this page is pure UI, no data wiring.
"""

import streamlit as st

from frontend.components.theme import page_header, placeholder_card
from frontend.config.constants import (
    HOME_DASHBOARD_PLACEHOLDER,
    HOME_EYEBROW,
    HOME_STAT_LABELS,
    HOME_SUBTITLE,
    HOME_TITLE,
)


def render() -> None:
    """Renders the Home page."""
    page_header(
        title=HOME_TITLE,
        subtitle=HOME_SUBTITLE,
        eyebrow=HOME_EYEBROW,
    )

    # Quick-glance summary chips (static placeholders for now)
    columns = st.columns(len(HOME_STAT_LABELS))
    for column, label in zip(columns, HOME_STAT_LABELS):
        with column:
            st.markdown(
                f"<div class='gv-chip'><span class='gv-chip-value'>—</span>"
                f"<span class='gv-chip-label'>{label}</span></div>",
                unsafe_allow_html=True,
            )

    st.write("")  # spacing
    st.divider()

    # Main dashboard placeholder
    placeholder_card(icon="📊", text=HOME_DASHBOARD_PLACEHOLDER)
