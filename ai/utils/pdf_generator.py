"""
pdf_generator.py
------------------
Complaint PDF export utility for GramVaani AI, built entirely on
`reportlab`.

Given a generated complaint dict and its recommended government
schemes, this module renders a professionally formatted, single-page
(or multi-page, if content is long) PDF report suitable for the
citizen to download and keep as a record, or submit alongside a
physical complaint.

The PDF includes, in order:
    - GramVaani AI header / report title
    - Complaint ID
    - Date
    - Complaint Type
    - Department
    - Priority
    - Summary
    - Formal Complaint
    - Recommended Government Schemes (name, description, eligibility,
      responsible department for each scheme, or a "no direct scheme
      found" note)

This is entirely offline / local:
    - No external API calls of any kind.
    - No network access required.
    - Uses only the `reportlab` library plus the Python standard
      library.

This module is intentionally framework-agnostic (no Streamlit
imports) so it can be reused outside the UI later - e.g. from
`backend/services` or a future API layer - without modification.

Public API:
    generate_complaint_pdf(complaint, schemes) -> bytes
"""

import logging
from datetime import date
from io import BytesIO
from typing import Any, Dict, List, Union

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
# A dedicated, namespaced logger, consistent with the rest of the
# `ai` package (see ai/llm/complaint_generator.py, ai/schemes/
# scheme_recommender.py, ai/utils/complaint_id.py).
logger = logging.getLogger("gramvaani.ai.utils.pdf_generator")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------
# Brand colors, kept consistent with frontend/components/theme.py
# ----------------------------------------------------------------------
_COLOR_NAVY = colors.HexColor("#0B1F3A")
_COLOR_TEAL = colors.HexColor("#0F9D8C")
_COLOR_TEAL_SOFT = colors.HexColor("#E6F5F3")
_COLOR_TEXT_MUTED = colors.HexColor("#5C6B7A")
_COLOR_BORDER = colors.HexColor("#E4E8EE")

_NO_SCHEME_FOUND_MESSAGE = "No direct government scheme found."


def _build_styles() -> Dict[str, ParagraphStyle]:
    """
    Builds the paragraph styles used throughout the PDF, layered on
    top of reportlab's default stylesheet.

    Returns:
        A dict of style name -> ParagraphStyle.
    """
    base = getSampleStyleSheet()

    styles: Dict[str, ParagraphStyle] = {
        "ReportTitle": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=_COLOR_NAVY,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "ReportSubtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=_COLOR_TEXT_MUTED,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "SectionHeading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=_COLOR_NAVY,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "FieldLabel": ParagraphStyle(
            "FieldLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=_COLOR_NAVY,
            leading=14,
        ),
        "FieldValue": ParagraphStyle(
            "FieldValue",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#1A1A1A"),
            leading=14,
        ),
        "SchemeName": ParagraphStyle(
            "SchemeName",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            textColor=_COLOR_NAVY,
            spaceBefore=8,
            leading=14,
        ),
        "SchemeField": ParagraphStyle(
            "SchemeField",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=colors.HexColor("#1A1A1A"),
            leading=13,
        ),
        "FooterNote": ParagraphStyle(
            "FooterNote",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=_COLOR_TEXT_MUTED,
            alignment=TA_CENTER,
            spaceBefore=18,
        ),
    }
    return styles


def _escape(value: Any) -> str:
    """
    Converts a value to a string and escapes the handful of
    characters that are meaningful to reportlab's Paragraph markup
    (which uses a small subset of HTML/XML), so field values from the
    LLM response are never mis-rendered or able to inject markup.

    Args:
        value: Any value to render as PDF text.

    Returns:
        A safe string for use inside a reportlab Paragraph.
    """
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _build_field_table(rows: List[List[str]], styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Builds a two-column label/value table for the core complaint
    fields, giving the PDF a clean, professional, aligned layout
    instead of loose paragraphs.

    Args:
        rows: List of [label, value] string pairs.
        styles: The style dict from `_build_styles()`.

    Returns:
        A configured reportlab Table flowable.
    """
    table_data = [
        [Paragraph(_escape(label), styles["FieldLabel"]),
         Paragraph(_escape(value), styles["FieldValue"])]
        for label, value in rows
    ]

    table = Table(table_data, colWidths=[4.2 * cm, 12.3 * cm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def generate_complaint_pdf(
    complaint: Dict[str, Any],
    schemes: Union[List[Dict[str, str]], str, None] = None,
) -> bytes:
    """
    Renders a professionally formatted PDF report for a generated
    complaint, including its recommended government schemes.

    Args:
        complaint: The complaint dict as produced by
            `ai/llm/complaint_generator.py` (plus the "complaint_id"
            field attached by `ai/utils/complaint_id.py`). Expected
            keys: "complaint_id", "complaint_type", "department",
            "priority", "summary", "formal_complaint". A missing
            "generated_date" falls back to today's date. Any missing
            key renders as an empty value rather than raising.
        schemes: Either a list of scheme dicts (each with "name",
            "description", "eligibility", "official_department"), the
            literal string "No direct government scheme found.", or
            None if no scheme lookup was performed.

    Returns:
        The PDF file content as raw bytes, ready to be offered for
        download (e.g. via `st.download_button`).
    """
    styles = _build_styles()
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="GramVaani AI Complaint Report",
    )

    story: List[Any] = []

    # --- Header ---
    story.append(Paragraph("GramVaani AI", styles["ReportTitle"]))
    story.append(Paragraph("Citizen Complaint Report", styles["ReportSubtitle"]))
    story.append(
        HRFlowable(width="100%", thickness=1.2, color=_COLOR_TEAL, spaceAfter=10)
    )

    # --- Core complaint fields ---
    complaint_id = complaint.get("complaint_id", "") or "N/A"
    generated_date = complaint.get("generated_date") or date.today().strftime(
        "%d %B %Y"
    )

    field_rows = [
        ("Complaint ID", complaint_id),
        ("Date", generated_date),
        ("Complaint Type", complaint.get("complaint_type", "")),
        ("Department", complaint.get("department", "")),
        ("Priority", complaint.get("priority", "")),
    ]
    story.append(_build_field_table(field_rows, styles))

    story.append(Paragraph("Summary", styles["SectionHeading"]))
    story.append(
        Paragraph(_escape(complaint.get("summary", "")), styles["FieldValue"])
    )

    story.append(Paragraph("Formal Complaint", styles["SectionHeading"]))
    story.append(
        Paragraph(
            _escape(complaint.get("formal_complaint", "")), styles["FieldValue"]
        )
    )

    # --- Recommended government schemes ---
    story.append(Paragraph("Recommended Government Schemes", styles["SectionHeading"]))
    story.append(
        HRFlowable(width="100%", thickness=0.6, color=_COLOR_BORDER, spaceAfter=6)
    )

    if not schemes or isinstance(schemes, str):
        message = schemes if isinstance(schemes, str) else _NO_SCHEME_FOUND_MESSAGE
        story.append(Paragraph(_escape(message), styles["FieldValue"]))
    else:
        for scheme in schemes:
            story.append(
                Paragraph(_escape(scheme.get("name", "")), styles["SchemeName"])
            )
            story.append(
                Paragraph(
                    f"<b>Description:</b> {_escape(scheme.get('description', ''))}",
                    styles["SchemeField"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Eligibility:</b> {_escape(scheme.get('eligibility', ''))}",
                    styles["SchemeField"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Responsible Department:</b> "
                    f"{_escape(scheme.get('official_department', ''))}",
                    styles["SchemeField"],
                )
            )
            story.append(
                HRFlowable(
                    width="100%", thickness=0.4, color=_COLOR_BORDER, spaceBefore=8
                )
            )

    # --- Footer ---
    story.append(Spacer(1, 0.4 * cm))
    story.append(
        Paragraph(
            "Generated automatically by GramVaani AI - Voice of the Citizen.",
            styles["FooterNote"],
        )
    )

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info(
        "Generated complaint PDF for Complaint ID '%s' (%d bytes).",
        complaint_id,
        len(pdf_bytes),
    )
    return pdf_bytes
