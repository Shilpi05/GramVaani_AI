"""
home.py
--------
Home / landing page for GramVaani AI.

This is a purely presentational redesign - no backend, AI, or
tracking logic is added or modified here. The only "live" data on
this page is the Statistics section, which READS the existing mock
complaint-tracking registry (`ai/utils/complaint_tracker.py`,
populated by `frontend/pages/file_complaint.py`) to show session
activity counts. Nothing on this page writes to that registry, and
no other module's logic is touched.

Sections, top to bottom:
    1. Hero - headline, subheadline, trust badges, primary/secondary CTAs
    2. Statistics - live, session-only complaint counts
    3. Voice Complaint Workflow - the 4-step technical pipeline
    4. Features - a 6-card capability grid
    5. How It Works - a simple 3-step citizen-facing journey
    6. Closing CTA banner

All CSS here is scoped under the `gv-home-` class prefix and injected
locally by this page only, so it cannot affect the appearance of any
other page. Every color used comes from `frontend/components/theme.py`
- no hex codes are hardcoded in this file. The app's overall theme
(light/dark base, canvas color) is pinned explicitly in
`.streamlit/config.toml`, so this page no longer needs its own
OS-dark-mode override - every visitor sees the same design regardless
of their system color scheme, consistent with every other page.
"""

import streamlit as st

from ai.utils.complaint_tracker import (
    SESSION_STATE_REGISTRY_KEY,
    STATUS_STAGES,
    compute_status,
)
from frontend.components.theme import (
    COLOR_BORDER,
    COLOR_NAVY,
    COLOR_NAVY_SOFT,
    COLOR_TEAL,
    COLOR_TEAL_DARK,
    COLOR_TEAL_SOFT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ON_NAVY,
    COLOR_TEXT_ON_NAVY_MUTED,
    COLOR_TEXT_ON_TEAL,
    COLOR_WHITE,
    RADIUS_LG,
)
from frontend.config.constants import (
    HOME_CTA_BANNER_TARGET_PAGE,
    HOME_HERO_PRIMARY_CTA_TARGET_PAGE,
    HOME_HERO_SECONDARY_CTA_TARGET_PAGE,
)
from frontend.utils.helpers import navigate_to
from frontend.utils.i18n import t

# ----------------------------------------------------------------------
# Scoped CSS for this page only (class prefix: gv-home-).
#
# All 4 grid-card types below (.gv-home-card, .gv-home-stat-card,
# .gv-home-workflow-step, .gv-home-how-step) deliberately share the
# same padding (1.5rem) and border-radius ({RADIUS_LG}) - they're the
# same visual component (white bordered card in a grid) reused across
# 4 sections, so they should look identical regardless of which
# section they're in.
#
# NOTE on .gv-home-hero-title's `!important`: Streamlit applies its
# own default color to every <h1> (sourced from .streamlit/config.toml's
# textColor = navy), which has higher CSS specificity than a
# page-scoped class alone. That default is invisible everywhere else
# in the app because the only other <h1> (page titles, via
# theme.py's page_header()) is ALSO meant to be navy and sits on a
# light background - so the override was silently winning without
# ever looking wrong, until this one h1, which needs to be white on
# the dark hero background. Same underlying issue, same fix already
# used in theme.py (see the sidebar button color rule).
# ----------------------------------------------------------------------
_HOME_STYLE = (
    "<style>"
    ".gv-home-hero{"
    f"background:linear-gradient(135deg,{COLOR_NAVY} 0%,{COLOR_NAVY_SOFT} 55%,{COLOR_TEAL} 160%);"
    "border-radius:20px;padding:2.75rem 2.5rem;margin-bottom:1.75rem;"
    "box-shadow:0 8px 24px rgba(11,31,58,0.18);"
    "}"
    ".gv-home-hero-eyebrow{"
    f"display:inline-block;background:rgba(255,255,255,0.14);color:{COLOR_TEXT_ON_TEAL};"
    "font-size:0.78rem;font-weight:600;letter-spacing:0.4px;text-transform:uppercase;"
    "padding:0.35rem 0.9rem;border-radius:999px;margin-bottom:1rem;"
    "}"
    ".gv-home-hero-title{"
    f"color:{COLOR_WHITE} !important;font-size:2.6rem;font-weight:800;line-height:1.15;"
    "margin:0 0 0.9rem 0;letter-spacing:-0.5px;"
    "}"
    ".gv-home-hero-subtitle{"
    f"color:{COLOR_TEXT_ON_NAVY_MUTED};font-size:1.08rem;line-height:1.6;max-width:760px;margin:0 0 1.4rem 0;"
    "}"
    ".gv-home-trust-row{display:flex;flex-wrap:wrap;gap:0.6rem;margin-top:0.4rem;}"
    ".gv-home-trust-pill{"
    "display:inline-flex;align-items:center;gap:0.4rem;background:rgba(255,255,255,0.10);"
    f"border:1px solid rgba(255,255,255,0.20);color:{COLOR_TEXT_ON_NAVY};font-size:0.82rem;font-weight:600;"
    "padding:0.4rem 0.85rem;border-radius:999px;"
    "}"
    ".gv-home-section{margin:2.6rem 0 1.2rem 0;}"
    ".gv-home-section-eyebrow{"
    f"display:inline-block;background:{COLOR_TEAL_SOFT};color:{COLOR_TEAL};"
    "font-size:0.75rem;font-weight:700;letter-spacing:0.4px;text-transform:uppercase;"
    "padding:0.3rem 0.75rem;border-radius:999px;margin-bottom:0.6rem;"
    "}"
    ".gv-home-section-title{"
    f"color:{COLOR_NAVY};font-size:1.65rem;font-weight:800;margin:0 0 0.35rem 0;"
    "}"
    ".gv-home-section-subtitle{"
    f"color:{COLOR_TEXT_MUTED};font-size:0.98rem;line-height:1.55;max-width:720px;margin:0 0 1.4rem 0;"
    "}"
    ".gv-home-grid{display:grid;gap:1.1rem;}"
    ".gv-home-grid-2{grid-template-columns:repeat(2,1fr);}"
    ".gv-home-grid-3{grid-template-columns:repeat(3,1fr);}"
    ".gv-home-grid-4{grid-template-columns:repeat(4,1fr);}"
    "@media (max-width:1100px){.gv-home-grid-3,.gv-home-grid-4{grid-template-columns:repeat(2,1fr);}}"
    "@media (max-width:680px){.gv-home-grid-2,.gv-home-grid-3,.gv-home-grid-4{grid-template-columns:1fr;}}"
    ".gv-home-card{"
    f"background-color:{COLOR_WHITE};border:1px solid {COLOR_BORDER};border-radius:{RADIUS_LG};"
    "padding:1.5rem;box-shadow:0 1px 3px rgba(11,31,58,0.06);transition:box-shadow 0.15s ease,transform 0.15s ease;"
    "}"
    ".gv-home-card:hover{box-shadow:0 8px 20px rgba(11,31,58,0.12);transform:translateY(-2px);}"
    ".gv-home-icon-badge{"
    f"width:46px;height:46px;border-radius:12px;background-color:{COLOR_TEAL_SOFT};"
    "display:flex;align-items:center;justify-content:center;font-size:1.4rem;margin-bottom:0.9rem;"
    "}"
    ".gv-home-card-title{"
    f"color:{COLOR_NAVY};font-size:1.05rem;font-weight:700;margin:0 0 0.4rem 0;"
    "}"
    ".gv-home-card-text{"
    f"color:{COLOR_TEXT_MUTED};font-size:0.9rem;line-height:1.5;margin:0;"
    "}"
    ".gv-home-stat-card{"
    f"background-color:{COLOR_WHITE};border:1px solid {COLOR_BORDER};border-radius:{RADIUS_LG};"
    "padding:1.5rem;box-shadow:0 1px 3px rgba(11,31,58,0.06);"
    "display:flex;align-items:center;gap:0.9rem;"
    "}"
    ".gv-home-stat-icon{"
    f"width:44px;height:44px;border-radius:999px;background-color:{COLOR_TEAL_SOFT};"
    "display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0;"
    "}"
    ".gv-home-stat-value{"
    f"color:{COLOR_NAVY};font-size:1.75rem;font-weight:800;line-height:1.1;display:block;"
    "}"
    ".gv-home-stat-label{"
    f"color:{COLOR_TEXT_MUTED};font-size:0.8rem;font-weight:600;margin-top:0.15rem;"
    "}"
    ".gv-home-workflow-step{"
    f"background-color:{COLOR_WHITE};border:1px solid {COLOR_BORDER};border-radius:{RADIUS_LG};"
    "padding:1.5rem;text-align:center;position:relative;"
    "}"
    ".gv-home-workflow-icon{"
    f"width:50px;height:50px;border-radius:999px;background-color:{COLOR_NAVY};"
    f"color:{COLOR_WHITE};"
    "display:flex;align-items:center;justify-content:center;font-size:1.4rem;"
    "margin:0 auto 0.8rem auto;"
    "}"
    ".gv-home-workflow-step-number{"
    f"color:{COLOR_TEAL};font-size:0.72rem;font-weight:800;letter-spacing:0.5px;"
    "text-transform:uppercase;margin-bottom:0.3rem;"
    "}"
    ".gv-home-workflow-title{"
    f"color:{COLOR_NAVY};font-size:0.98rem;font-weight:700;margin:0 0 0.35rem 0;"
    "}"
    ".gv-home-workflow-text{"
    f"color:{COLOR_TEXT_MUTED};font-size:0.85rem;line-height:1.45;margin:0;"
    "}"
    ".gv-home-how-step{"
    f"background-color:{COLOR_WHITE};border:1px solid {COLOR_BORDER};border-radius:{RADIUS_LG};"
    "padding:1.5rem;"
    "}"
    ".gv-home-how-step-number{"
    f"width:38px;height:38px;border-radius:999px;background-color:{COLOR_TEAL};color:{COLOR_WHITE};"
    "display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:800;"
    "margin-bottom:0.9rem;"
    "}"
    ".gv-home-how-title{"
    f"color:{COLOR_NAVY};font-size:1.05rem;font-weight:700;margin:0 0 0.4rem 0;"
    "}"
    ".gv-home-how-text{"
    f"color:{COLOR_TEXT_MUTED};font-size:0.9rem;line-height:1.5;margin:0;"
    "}"
    ".gv-home-cta-banner{"
    f"background:linear-gradient(120deg,{COLOR_TEAL} 0%,{COLOR_TEAL_DARK} 100%);border-radius:18px;"
    "padding:2.2rem 2.4rem;margin:2.6rem 0 1rem 0;display:flex;align-items:center;"
    "justify-content:space-between;flex-wrap:wrap;gap:1rem;"
    "}"
    f'.gv-home-cta-banner-title{{color:{COLOR_WHITE};font-size:1.35rem;font-weight:800;margin:0 0 0.25rem 0;}}'
    f'.gv-home-cta-banner-subtitle{{color:{COLOR_TEXT_ON_TEAL};font-size:0.92rem;margin:0;}}'
    "</style>"
)


def _get_session_stats() -> dict:
    """
    Computes live, session-only complaint counts from the existing
    mock complaint tracking registry. Read-only: does not write to
    `st.session_state` and does not alter `ai/utils/complaint_tracker.py`
    in any way.

    Returns:
        A dict with "filed", "in_progress", and "resolved" integer
        counts for the current browser session.
    """
    registry = st.session_state.get(SESSION_STATE_REGISTRY_KEY, {})

    filed = len(registry)
    resolved = 0
    in_progress = 0

    for record in registry.values():
        status = compute_status(record.get("generated_at", ""))
        if status == STATUS_STAGES[-1]:  # "Resolved"
            resolved += 1
        elif status != STATUS_STAGES[0]:  # "Under Review" or "Assigned"
            in_progress += 1

    return {"filed": filed, "in_progress": in_progress, "resolved": resolved}


def _render_hero() -> None:
    """Renders the hero section: headline, subheadline, trust badges."""
    trust_pills = "".join(
        f'<span class="gv-home-trust-pill">{badge["icon"]} {badge["label"]}</span>'
        for badge in t("home.hero.trust_badges")
    )

    hero_html = (
        '<div class="gv-home-hero">'
        f'<span class="gv-home-hero-eyebrow">{t("home.hero.eyebrow")}</span>'
        f'<h1 class="gv-home-hero-title">{t("home.hero.headline")}</h1>'
        f'<p class="gv-home-hero-subtitle">{t("home.hero.subheadline")}</p>'
        f'<div class="gv-home-trust-row">{trust_pills}</div>'
        "</div>"
    )
    st.markdown(_HOME_STYLE + hero_html, unsafe_allow_html=True)

    cta_col1, cta_col2, _spacer = st.columns([1, 1, 2])
    with cta_col1:
        if st.button(
            t("home.hero.primary_cta_label"),
            use_container_width=True,
            type="primary",
            key="gv_home_hero_primary_cta",
        ):
            navigate_to(HOME_HERO_PRIMARY_CTA_TARGET_PAGE)
    with cta_col2:
        if st.button(
            t("home.hero.secondary_cta_label"),
            use_container_width=True,
            key="gv_home_hero_secondary_cta",
        ):
            navigate_to(HOME_HERO_SECONDARY_CTA_TARGET_PAGE)


def _render_section_header(eyebrow: str, title: str, subtitle: str) -> None:
    """Renders a consistent eyebrow + title + subtitle block for a section."""
    st.markdown(
        '<div class="gv-home-section">'
        f'<span class="gv-home-section-eyebrow">{eyebrow}</span>'
        f'<h2 class="gv-home-section-title">{title}</h2>'
        f'<p class="gv-home-section-subtitle">{subtitle}</p>'
        "</div>",
        unsafe_allow_html=True,
    )


def _render_statistics() -> None:
    """Renders the live, session-only Statistics section."""
    _render_section_header(
        t("home.stats.eyebrow"), t("home.stats.title"), t("home.stats.subtitle")
    )

    stats = _get_session_stats()
    stat_values = [stats["filed"], stats["in_progress"], stats["resolved"]]
    stat_icons = ["🧾", "⏳", "✅"]

    cards = "".join(
        '<div class="gv-home-stat-card">'
        f'<div class="gv-home-stat-icon">{icon}</div>'
        "<div>"
        f'<span class="gv-home-stat-value">{value}</span>'
        f'<div class="gv-home-stat-label">{label}</div>'
        "</div>"
        "</div>"
        for icon, value, label in zip(stat_icons, stat_values, t("home.stats.labels"))
    )

    st.markdown(
        f'<div class="gv-home-grid gv-home-grid-3">{cards}</div>',
        unsafe_allow_html=True,
    )


def _render_workflow() -> None:
    """Renders the Voice Complaint Workflow step strip."""
    _render_section_header(
        t("home.workflow.eyebrow"), t("home.workflow.title"), t("home.workflow.subtitle")
    )

    step_label = t("home.workflow.step_label")
    steps = "".join(
        '<div class="gv-home-workflow-step">'
        f'<div class="gv-home-workflow-step-number">{step_label} {index + 1}</div>'
        f'<div class="gv-home-workflow-icon">{step["icon"]}</div>'
        f'<div class="gv-home-workflow-title">{step["title"]}</div>'
        f'<p class="gv-home-workflow-text">{step["text"]}</p>'
        "</div>"
        for index, step in enumerate(t("home.workflow.steps"))
    )

    st.markdown(
        f'<div class="gv-home-grid gv-home-grid-4">{steps}</div>',
        unsafe_allow_html=True,
    )


def _render_features() -> None:
    """Renders the Features capability grid."""
    _render_section_header(
        t("home.features.eyebrow"), t("home.features.title"), t("home.features.subtitle")
    )

    cards = "".join(
        '<div class="gv-home-card">'
        f'<div class="gv-home-icon-badge">{feature["icon"]}</div>'
        f'<div class="gv-home-card-title">{feature["title"]}</div>'
        f'<p class="gv-home-card-text">{feature["text"]}</p>'
        "</div>"
        for feature in t("home.features.items")
    )

    st.markdown(
        f'<div class="gv-home-grid gv-home-grid-3">{cards}</div>',
        unsafe_allow_html=True,
    )


def _render_how_it_works() -> None:
    """Renders the citizen-facing How It Works steps."""
    _render_section_header(
        t("home.how_it_works.eyebrow"),
        t("home.how_it_works.title"),
        t("home.how_it_works.subtitle"),
    )

    steps = "".join(
        '<div class="gv-home-how-step">'
        f'<div class="gv-home-how-step-number">{index + 1}</div>'
        f'<div class="gv-home-how-title">{step["title"]}</div>'
        f'<p class="gv-home-how-text">{step["text"]}</p>'
        "</div>"
        for index, step in enumerate(t("home.how_it_works.steps"))
    )

    st.markdown(
        f'<div class="gv-home-grid gv-home-grid-3">{steps}</div>',
        unsafe_allow_html=True,
    )


def _render_cta_banner() -> None:
    """Renders the closing call-to-action banner with a navigation button."""
    st.markdown(
        '<div class="gv-home-cta-banner">'
        "<div>"
        f'<p class="gv-home-cta-banner-title">{t("home.cta_banner.title")}</p>'
        f'<p class="gv-home-cta-banner-subtitle">{t("home.cta_banner.subtitle")}</p>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    button_col, _spacer = st.columns([1, 3])
    with button_col:
        if st.button(
            t("home.cta_banner.button_label"),
            use_container_width=True,
            type="primary",
            key="gv_home_cta_banner_button",
        ):
            navigate_to(HOME_CTA_BANNER_TARGET_PAGE)


def render() -> None:
    """Renders the redesigned Home page."""
    _render_hero()

    st.write("")
    _render_statistics()

    st.write("")
    _render_workflow()

    st.write("")
    _render_features()

    st.write("")
    _render_how_it_works()

    _render_cta_banner()