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

import html

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

# Dark-mode surface tokens - used only for the main content area's
# background/cards when the citizen selects "Dark" in Settings. The
# sidebar and hero/CTA banner gradients are brand-colored and stay
# navy/teal regardless of this setting (same reasoning many products
# use for a colored header/nav that doesn't follow light/dark mode).
# Text-on-dark reuses COLOR_TEXT_ON_NAVY / COLOR_TEXT_ON_NAVY_MUTED
# above rather than introducing yet more near-duplicate tokens.
COLOR_DARK_BG: str = "#0B1626"
COLOR_DARK_CARD: str = "#13233C"
COLOR_DARK_BORDER: str = "#24384F"
COLOR_DARK_BADGE_MEDIUM_BG: str = "#1C3350"

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
RADIUS_LG: str = "14px"
RADIUS_PILL: str = "999px"


def inject_global_styles(dark_mode: bool = False) -> None:
    """
    Injects global CSS used across every page of the app.

    Args:
        dark_mode: When True, swaps the main content area's surface
            colors (page background, card background/border, primary
            and muted text, badge fills) to dark equivalents. The
            sidebar and the hero/CTA banner gradients are brand
            chrome and intentionally stay navy/teal regardless of
            this setting - only content-area surfaces toggle. Set via
            the "Theme" preference on the Settings page.
    """
    if dark_mode:
        surface_bg = COLOR_DARK_BG
        card_bg = COLOR_DARK_CARD
        card_border = COLOR_DARK_BORDER
        text_primary = COLOR_TEXT_ON_NAVY
        text_muted = COLOR_TEXT_ON_NAVY_MUTED
        badge_high_bg = COLOR_TEAL
        badge_high_text = COLOR_DARK_BG
        badge_medium_bg = COLOR_DARK_BADGE_MEDIUM_BG
    else:
        surface_bg = COLOR_BG
        card_bg = COLOR_WHITE
        card_border = COLOR_BORDER
        text_primary = COLOR_NAVY
        text_muted = COLOR_TEXT_MUTED
        badge_high_bg = COLOR_NAVY
        badge_high_text = COLOR_WHITE
        badge_medium_bg = COLOR_TEAL_SOFT

    st.markdown(
        f"""
        <style>
            /* ---------- Base ---------- */
            html, body, [class*="css"] {{
                font-family: {FONT_STACK};
            }}

            .main {{
                background-color: {surface_bg};
            }}

            /* ---------- Sidebar ----------
               Brand chrome - always navy, regardless of the content
               area's light/dark mode setting. */
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
                color: {text_primary};
                font-size: {FONT_SIZE_PAGE_TITLE};
                font-weight: 700;
                margin-bottom: 0.1rem;
            }}

            .gv-page-subtitle {{
                color: {text_muted};
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
                background-color: {card_bg};
                border: 1px solid {card_border};
                border-radius: {RADIUS_LG};
                padding: {SPACING_LG};
                box-shadow: 0 1px 2px rgba(11, 31, 58, 0.04);
            }}

            .gv-card h3 {{
                color: {text_primary};
                font-size: {FONT_SIZE_CARD_TITLE};
                margin-top: 0;
            }}

            .gv-card p {{
                color: {text_muted};
            }}

            /* Same visual weight as .gv-card h3, for headings that
               sit above a group of cards rather than inside one
               (e.g. "Recommended Government Schemes" above a stack
               of individual scheme cards). */
            .gv-section-title {{
                color: {text_primary};
                font-size: {FONT_SIZE_CARD_TITLE};
                font-weight: 700;
                margin: 0 0 {SPACING_SM} 0;
            }}

            .gv-placeholder-card {{
                background-color: {card_bg};
                border: 1.5px dashed {card_border};
                border-radius: {RADIUS_LG};
                padding: {SPACING_XL} 2rem;
                text-align: center;
                color: {text_muted};
            }}

            .gv-placeholder-card .gv-placeholder-icon {{
                font-size: 2rem;
                margin-bottom: {SPACING_SM};
            }}

            /* ---------- Field badges (priority, department) ----------
               Priority is differentiated by fill *intensity* (navy ->
               teal-soft -> outlined) rather than hue, deliberately
               staying inside the existing navy/teal palette instead
               of introducing a traffic-light color system. Fills
               swap to dark-mode-appropriate equivalents above so
               "High" still stands out against a dark card instead of
               blending into it. */
            .gv-badge {{
                display: inline-block;
                border-radius: {RADIUS_PILL};
                padding: 0.25rem 0.75rem;
                font-size: 0.78rem;
                font-weight: 600;
            }}

            .gv-badge-priority-high {{
                background-color: {badge_high_bg};
                color: {badge_high_text};
            }}

            .gv-badge-priority-medium {{
                background-color: {badge_medium_bg};
                color: {COLOR_TEAL};
            }}

            .gv-badge-priority-low {{
                background-color: {card_bg};
                color: {text_muted};
                border: 1px solid {card_border};
            }}

            .gv-badge-department {{
                background-color: {surface_bg};
                color: {text_primary};
                border: 1px solid {card_border};
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


_PRIORITY_BADGE_VARIANTS = {
    "high": "gv-badge-priority-high",
    "medium": "gv-badge-priority-medium",
    "low": "gv-badge-priority-low",
}


def priority_badge_html(priority: str) -> str:
    """
    Builds a self-contained HTML `<span>` badge for a complaint
    priority level, styled by severity (fill intensity, not hue - see
    the `.gv-badge-priority-*` rules in `inject_global_styles()`).

    Shared by every page that displays a complaint's priority
    (`frontend/pages/file_complaint.py`,
    `frontend/pages/track_complaint.py`) so the High/Medium/Low ->
    CSS class mapping exists in exactly one place.

    Args:
        priority: Expected to be "High", "Medium", or "Low" (see
            `ai/llm/prompts.py`), but any value is accepted - an
            unrecognized value still renders, just with the neutral
            "medium" styling rather than failing.

    Returns:
        An HTML string, safe to splice directly into an f-string
        already marked `unsafe_allow_html=True` - the priority text
        itself is escaped here.
    """
    variant = _PRIORITY_BADGE_VARIANTS.get(
        str(priority).strip().lower(), "gv-badge-priority-medium"
    )
    return f'<span class="gv-badge {variant}">{html.escape(str(priority))}</span>'


def department_badge_html(department: str) -> str:
    """
    Builds a self-contained HTML `<span>` badge for a department name.
    Shared for the same reason as `priority_badge_html()` above.

    Args:
        department: The department name to display.

    Returns:
        An HTML string, safe to splice directly into an f-string
        already marked `unsafe_allow_html=True`.
    """
    return f'<span class="gv-badge gv-badge-department">{html.escape(str(department))}</span>'


def info_row_html(label: str, value: str) -> str:
    """
    Builds a single "label: value" row for a read-only info card
    (e.g. the "Application Information" section on the Settings
    page). Centralized here, rather than written inline per page, so
    every such row shares identical spacing/typography.

    Args:
        label: The field name (e.g. "Version").
        value: The field's current value (e.g. "v1.0").

    Returns:
        An HTML string, safe to splice directly into an f-string
        already marked `unsafe_allow_html=True` - both label and
        value are escaped here.
    """
    return (
        '<p style="margin:0.35rem 0;">'
        f"<strong>{html.escape(str(label))}:</strong> "
        f"{html.escape(str(value))}"
        "</p>"
    )