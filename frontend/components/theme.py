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

# Success tokens - used narrowly for the "Resolved" state on the Track
# Complaint page (resolved status badge, final timeline marker, the
# "Resolved Successfully" confirmation banner). Every other status in
# the app stays inside the navy/teal palette; a small, deliberate
# green accent is added only for this one terminal, positive state,
# which is a common and easily-recognized convention on government
# status-tracking portals.
COLOR_SUCCESS: str = "#1E8E5A"
COLOR_SUCCESS_SOFT: str = "#E7F6EE"
COLOR_DARK_SUCCESS_SOFT: str = "#123524"

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
        success_soft_bg = COLOR_DARK_SUCCESS_SOFT
    else:
        surface_bg = COLOR_BG
        card_bg = COLOR_WHITE
        card_border = COLOR_BORDER
        text_primary = COLOR_NAVY
        text_muted = COLOR_TEXT_MUTED
        badge_high_bg = COLOR_NAVY
        badge_high_text = COLOR_WHITE
        badge_medium_bg = COLOR_TEAL_SOFT
        success_soft_bg = COLOR_SUCCESS_SOFT

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

            /* ---------- Status badge (Current Status field) ----------
               Same pill shape as .gv-badge, but colored per pipeline
               stage instead of per priority. Stays in the navy/teal
               palette for every stage except the terminal "Resolved"
               state, which uses the small success accent above. */
            .gv-status-badge {{
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                border-radius: {RADIUS_PILL};
                padding: 0.3rem 0.85rem;
                font-size: 0.8rem;
                font-weight: 700;
            }}

            .gv-status-badge-dot {{
                width: 7px;
                height: 7px;
                border-radius: {RADIUS_PILL};
                background-color: currentColor;
                flex-shrink: 0;
            }}

            .gv-status-badge-submitted {{
                background-color: {surface_bg};
                color: {text_muted};
                border: 1px solid {card_border};
            }}

            .gv-status-badge-under-review {{
                background-color: {badge_medium_bg};
                color: {COLOR_TEAL};
            }}

            .gv-status-badge-assigned {{
                background-color: {COLOR_NAVY};
                color: {COLOR_WHITE};
            }}

            .gv-status-badge-resolved {{
                background-color: {success_soft_bg};
                color: {COLOR_SUCCESS};
            }}

            /* ---------- Status timeline (Track Complaint) ----------
               A vertical timeline: each stage shows its label plus
               (once reached) the date/time it was reached, connected
               by a downward arrow - closer to how a real grievance
               portal lays out a complaint's history than a row of
               bare circles. The current stage gets a teal-highlighted
               label and marker plus a small "Current Stage" tag
               (reusing .gv-eyebrow's existing teal-soft pill styling
               below, not a new color) so it's unambiguous at a
               glance which stage the complaint is in right now. */
            .gv-vtimeline {{
                display: flex;
                flex-direction: column;
                margin: 1.1rem 0 0.25rem 0;
            }}

            .gv-vtimeline-row {{
                display: flex;
                align-items: center;
                gap: 0.65rem;
            }}

            .gv-vtimeline-marker {{
                width: 15px;
                height: 15px;
                border-radius: {RADIUS_PILL};
                flex-shrink: 0;
            }}

            .gv-vtimeline-item-done .gv-vtimeline-marker {{
                background-color: {COLOR_TEAL};
            }}

            .gv-vtimeline-item-done-final .gv-vtimeline-marker {{
                background-color: {COLOR_SUCCESS};
            }}

            .gv-vtimeline-item-current .gv-vtimeline-marker {{
                background-color: {card_bg};
                border: 3px solid {COLOR_TEAL};
                box-shadow: 0 0 0 4px {COLOR_TEAL_SOFT};
            }}

            .gv-vtimeline-item-upcoming .gv-vtimeline-marker {{
                background-color: {card_bg};
                border: 1.5px solid {card_border};
            }}

            .gv-vtimeline-label {{
                font-size: 0.95rem;
                font-weight: 700;
            }}

            .gv-vtimeline-item-done .gv-vtimeline-label,
            .gv-vtimeline-item-done-final .gv-vtimeline-label {{
                color: {text_primary};
            }}

            .gv-vtimeline-item-current .gv-vtimeline-label {{
                color: {COLOR_TEAL};
            }}

            .gv-vtimeline-item-upcoming .gv-vtimeline-label {{
                color: {text_muted};
                font-weight: 600;
            }}

            .gv-vtimeline-current-tag {{
                display: inline-block;
                background-color: {COLOR_TEAL_SOFT};
                color: {COLOR_TEAL};
                font-size: 0.68rem;
                font-weight: 700;
                letter-spacing: 0.3px;
                text-transform: uppercase;
                padding: 0.12rem 0.55rem;
                border-radius: {RADIUS_PILL};
                margin-left: 0.5rem;
            }}

            .gv-vtimeline-timestamp {{
                font-size: 0.8rem;
                color: {text_muted};
                margin: 0.15rem 0 0 1.75rem;
            }}

            .gv-vtimeline-connector {{
                color: {card_border};
                font-size: 1.05rem;
                line-height: 1;
                margin: 0.3rem 0 0.3rem 6px;
            }}

            .gv-vtimeline-connector-done {{
                color: {COLOR_TEAL};
            }}

            /* ---------- Info grid (Complaint ID, Submission Date, ... ---------- */
            .gv-info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
                gap: 0.85rem;
                margin-top: 1.1rem;
            }}

            .gv-info-item {{
                background-color: {surface_bg};
                border: 1px solid {card_border};
                border-radius: {RADIUS_SM};
                padding: 0.7rem 0.9rem;
            }}

            .gv-info-label {{
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.4px;
                color: {text_muted};
                font-weight: 700;
                margin-bottom: 0.3rem;
            }}

            .gv-info-value {{
                font-size: 0.95rem;
                color: {text_primary};
                font-weight: 600;
            }}

            .gv-info-value-sub {{
                font-size: 0.78rem;
                color: {text_muted};
                font-weight: 600;
                margin-top: 0.15rem;
            }}

            /* ---------- Resolved-Successfully confirmation banner ---------- */
            .gv-resolved-banner {{
                display: flex;
                align-items: flex-start;
                gap: 0.85rem;
                background-color: {success_soft_bg};
                border: 1px solid {COLOR_SUCCESS};
                border-radius: {RADIUS_LG};
                padding: 1rem 1.15rem;
                margin: 1.1rem 0 0.25rem 0;
            }}

            .gv-resolved-banner-icon {{
                font-size: 1.5rem;
                line-height: 1.4;
            }}

            .gv-resolved-banner-title {{
                color: {COLOR_SUCCESS};
                font-weight: 700;
                font-size: 1.02rem;
            }}

            .gv-resolved-banner-text {{
                color: {text_muted};
                font-size: 0.83rem;
                margin-top: 0.15rem;
            }}

            /* ---------- Empty state (invalid / not-found Complaint ID) ---------- */
            .gv-empty-state {{
                background-color: {card_bg};
                border: 1.5px dashed {card_border};
                border-radius: {RADIUS_LG};
                padding: 2.5rem 2rem;
                text-align: center;
            }}

            .gv-empty-state-icon {{
                font-size: 2.3rem;
                margin-bottom: 0.6rem;
            }}

            .gv-empty-state-title {{
                color: {text_primary};
                font-weight: 700;
                font-size: 1.1rem;
                margin-bottom: 0.4rem;
            }}

            .gv-empty-state-text {{
                color: {text_muted};
                font-size: 0.88rem;
                max-width: 440px;
                margin: 0 auto;
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


_STATUS_BADGE_VARIANTS = {
    "submitted": "gv-status-badge-submitted",
    "under review": "gv-status-badge-under-review",
    "assigned": "gv-status-badge-assigned",
    "resolved": "gv-status-badge-resolved",
}


def status_badge_html(status: str) -> str:
    """
    Builds a self-contained HTML `<span>` badge for a complaint's
    current pipeline status (Submitted / Under Review / Assigned /
    Resolved), colored per stage - the same "existing design system"
    pattern as `priority_badge_html()`, just keyed on status instead
    of priority. Used by the Track Complaint page's "Current Status"
    field.

    Args:
        status: Expected to be one of
            `ai.utils.complaint_tracker.STATUS_STAGES`, but any value
            is accepted - an unrecognized value still renders, with
            the neutral "submitted" styling.

    Returns:
        An HTML string, safe to splice directly into an f-string
        already marked `unsafe_allow_html=True` - the status text
        itself is escaped here.
    """
    variant = _STATUS_BADGE_VARIANTS.get(
        str(status).strip().lower(), "gv-status-badge-submitted"
    )
    return (
        f'<span class="gv-status-badge {variant}">'
        '<span class="gv-status-badge-dot"></span>'
        f"{html.escape(str(status))}</span>"
    )


def resolved_banner_html(confirmation_text: str) -> str:
    """
    Builds the "Resolved Successfully" confirmation banner shown on
    the Track Complaint page once a complaint's status reaches the
    final stage.

    Args:
        confirmation_text: Short supporting line shown under the
            title (e.g. a completion timestamp). Already expected to
            be plain text - it is escaped here.

    Returns:
        An HTML string, safe to splice directly into an f-string
        already marked `unsafe_allow_html=True`.
    """
    return (
        '<div class="gv-resolved-banner">'
        '<div class="gv-resolved-banner-icon">&#9989;</div>'
        "<div>"
        '<div class="gv-resolved-banner-title">Resolved Successfully</div>'
        f'<div class="gv-resolved-banner-text">{html.escape(confirmation_text)}</div>'
        "</div>"
        "</div>"
    )


def render_empty_state(icon: str, title: str, text: str) -> None:
    """
    Renders a professional empty-state card - used in place of a
    plain warning/error string when, for example, a Complaint ID
    doesn't match any tracked complaint. Visually distinct from
    `placeholder_card()` (which marks "not built yet" modules): this
    one signals "nothing found for your input", not "coming soon".

    Args:
        icon: A single emoji illustrating the empty state.
        title: Short heading (e.g. "Complaint Not Found").
        text: Supporting explanation shown under the title.
    """
    st.markdown(
        f"""
        <div class="gv-empty-state">
            <div class="gv-empty-state-icon">{icon}</div>
            <div class="gv-empty-state-title">{html.escape(title)}</div>
            <div class="gv-empty-state-text">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )