"""
theme.py
---------
Centralized visual identity for GramVaani AI.

This module owns everything related to *appearance*:
    - Color palette (design tokens)
    - Typography constants
    - Spacing constants
    - Global CSS injection
    - Reusable presentational helpers (page headers, placeholder cards)

Content (page titles, copy, labels) does NOT live here - see
`frontend/config/constants.py` for that. This separation means a
designer can restyle the entire app by editing only this file,
without ever touching page content.

Color system (kept deliberately minimal, per design spec):
    Navy   -> primary text / brand accents
    White  -> background / surfaces
    Teal   -> interactive accents (buttons, active states, highlights)
"""

import streamlit as st

# ----------------------------------------------------------------------
# Color palette - change these to re-theme the entire app
# ----------------------------------------------------------------------
COLOR_NAVY: str = "#0B1F3A"
COLOR_NAVY_SOFT: str = "#14294D"
COLOR_TEAL: str = "#0F9D8C"
COLOR_TEAL_SOFT: str = "#E6F5F3"
COLOR_WHITE: str = "#FFFFFF"
COLOR_BG: str = "#F7F9FB"
COLOR_BORDER: str = "#E4E8EE"
COLOR_TEXT_MUTED: str = "#5C6B7A"
COLOR_SIDEBAR_TAGLINE: str = "#B7C2D0"
COLOR_SIDEBAR_FOOTER: str = "#7C8CA0"

# Text-on-dark tokens - used on the navy/teal gradient surfaces (hero,
# CTA banner). Named and centralized here instead of being hardcoded
# per-page, so every dark surface in the app draws from the same
# palette rather than each page picking its own near-white shade.
COLOR_TEAL_DARK: str = "#0B8377"
COLOR_TEXT_ON_NAVY: str = "#F2F6FA"
COLOR_TEXT_ON_NAVY_MUTED: str = "#D7E2EE"
COLOR_TEXT_ON_TEAL: str = "#EAF6F4"

# ----------------------------------------------------------------------
# Typography constants
# ----------------------------------------------------------------------
FONT_STACK: str = (
    "'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, "
    "'Helvetica Neue', Arial, sans-serif"
)
FONT_SIZE_TAGLINE: str = "0.78rem"
FONT_SIZE_FOOTER: str = "0.7rem"
FONT_SIZE_SUBTITLE: str = "1.05rem"
FONT_SIZE_EYEBROW: str = "0.75rem"
FONT_SIZE_CHIP_VALUE: str = "1.4rem"
FONT_SIZE_CHIP_LABEL: str = "0.75rem"
# The two most-used headings in the app - every page's title (via
# page_header()) and every card's <h3> - previously had no explicit
# font-size at all and fell back to the browser's default h1/h3
# sizing. Every other text element in this file has a deliberate
# size; these are the last two gaps.
FONT_SIZE_PAGE_TITLE: str = "2rem"
FONT_SIZE_CARD_TITLE: str = "1.15rem"

# ----------------------------------------------------------------------
# Spacing constants
# ----------------------------------------------------------------------
SPACING_XS: str = "0.25rem"
SPACING_SM: str = "0.5rem"
SPACING_MD: str = "1rem"
SPACING_LG: str = "1.75rem"
SPACING_XL: str = "3rem"

# ----------------------------------------------------------------------
# Border radius constants
# ----------------------------------------------------------------------
RADIUS_SM: str = "8px"
RADIUS_MD: str = "10px"
RADIUS_LG: str = "14px"
RADIUS_PILL: str = "999px"


def inject_global_styles() -> None:
    """Injects global CSS used across every page of the app."""
    st.markdown(
        f"""
        <style>
            /* ---------- Base ---------- */
            html, body, [class*="css"] {{
                font-family: {FONT_STACK};
            }}

            .main {{
                background-color: {COLOR_BG};
            }}

            /* ---------- Sidebar ---------- */
            section[data-testid="stSidebar"] {{
                background-color: {COLOR_NAVY};
                border-right: 1px solid {COLOR_BORDER};
            }}

            section[data-testid="stSidebar"] * {{
                color: {COLOR_WHITE} !important;
            }}

            .gv-sidebar-brand {{
                display: flex;
                align-items: center;
                gap: {SPACING_SM};
                padding: {SPACING_SM} 0 0.1rem 0;
            }}

            .gv-sidebar-brand-icon {{
                font-size: 1.4rem;
            }}

            .gv-sidebar-brand-text {{
                font-size: 1.25rem;
                font-weight: 700;
                letter-spacing: 0.2px;
            }}

            .gv-sidebar-brand-text span {{
                color: {COLOR_TEAL};
            }}

            .gv-sidebar-tagline {{
                font-size: {FONT_SIZE_TAGLINE};
                color: {COLOR_SIDEBAR_TAGLINE} !important;
                margin-top: -6px;
                margin-bottom: {SPACING_SM};
            }}

            .gv-sidebar-footer {{
                font-size: {FONT_SIZE_FOOTER};
                color: {COLOR_SIDEBAR_FOOTER} !important;
                text-align: center;
            }}

            /* Sidebar nav buttons */
            section[data-testid="stSidebar"] button {{
                background-color: transparent !important;
                border: 1px solid transparent !important;
                text-align: left !important;
                justify-content: flex-start !important;
                font-weight: 500 !important;
                border-radius: {RADIUS_SM} !important;
            }}

            section[data-testid="stSidebar"] button:hover {{
                background-color: {COLOR_NAVY_SOFT} !important;
                border: 1px solid {COLOR_TEAL} !important;
            }}

            section[data-testid="stSidebar"] button[kind="primary"] {{
                background-color: {COLOR_TEAL} !important;
                border: 1px solid {COLOR_TEAL} !important;
                color: {COLOR_NAVY} !important;
                font-weight: 600 !important;
            }}

            section[data-testid="stSidebar"] button[kind="primary"] * {{
                color: {COLOR_NAVY} !important;
            }}

            /* ---------- Page header ---------- */
            .gv-page-title {{
                color: {COLOR_NAVY};
                font-size: {FONT_SIZE_PAGE_TITLE};
                font-weight: 700;
                margin-bottom: 0.1rem;
            }}

            .gv-page-subtitle {{
                color: {COLOR_TEXT_MUTED};
                font-size: {FONT_SIZE_SUBTITLE};
                margin-bottom: 1.5rem;
            }}

            .gv-eyebrow {{
                display: inline-block;
                background-color: {COLOR_TEAL_SOFT};
                color: {COLOR_TEAL};
                font-size: {FONT_SIZE_EYEBROW};
                font-weight: 600;
                letter-spacing: 0.4px;
                text-transform: uppercase;
                padding: {SPACING_XS} 0.65rem;
                border-radius: {RADIUS_PILL};
                margin-bottom: {SPACING_SM};
            }}

            /* ---------- Cards ---------- */
            .gv-card {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_BORDER};
                border-radius: {RADIUS_LG};
                padding: {SPACING_LG};
                box-shadow: 0 1px 2px rgba(11, 31, 58, 0.04);
            }}

            .gv-card h3 {{
                color: {COLOR_NAVY};
                font-size: {FONT_SIZE_CARD_TITLE};
                margin-top: 0;
            }}

            .gv-card p {{
                color: {COLOR_TEXT_MUTED};
            }}

            .gv-placeholder-card {{
                background-color: {COLOR_WHITE};
                border: 1.5px dashed {COLOR_BORDER};
                border-radius: {RADIUS_LG};
                padding: {SPACING_XL} 2rem;
                text-align: center;
                color: {COLOR_TEXT_MUTED};
            }}

            .gv-placeholder-card .gv-placeholder-icon {{
                font-size: 2rem;
                margin-bottom: {SPACING_SM};
            }}

            /* ---------- Stat chips ---------- */
            .gv-chip {{
                background-color: {COLOR_TEAL_SOFT};
                color: {COLOR_TEAL};
                border-radius: {RADIUS_MD};
                padding: 0.9rem {SPACING_MD};
                text-align: center;
                font-weight: 600;
            }}

            .gv-chip .gv-chip-value {{
                font-size: {FONT_SIZE_CHIP_VALUE};
                color: {COLOR_NAVY};
                display: block;
            }}

            .gv-chip .gv-chip-label {{
                font-size: {FONT_SIZE_CHIP_LABEL};
                color: {COLOR_TEXT_MUTED};
                font-weight: 500;
            }}

            /* Hide default Streamlit chrome for a cleaner look */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "", eyebrow: str = "") -> None:
    """
    Renders a consistent page header (eyebrow + title + subtitle)
    used at the top of every page.

    Args:
        title: The main page heading (required).
        subtitle: Optional supporting line shown under the title.
        eyebrow: Optional small label shown above the title.
    """
    if eyebrow:
        st.markdown(f"<span class='gv-eyebrow'>{eyebrow}</span>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='gv-page-title'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p class='gv-page-subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def placeholder_card(icon: str, text: str) -> None:
    """
    Renders a dashed placeholder card for modules not yet built.

    Args:
        icon: A single emoji representing the module.
        text: Short description of what will eventually live here.
    """
    st.markdown(
        f"""
        <div class="gv-placeholder-card">
            <div class="gv-placeholder-icon">{icon}</div>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )