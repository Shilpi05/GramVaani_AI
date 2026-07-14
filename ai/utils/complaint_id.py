"""
complaint_id.py
-----------------
Complaint ID generation utility for GramVaani AI.

Generates a unique, human-readable identifier for each complaint, in
the format:

    GV-YYYYMMDD-NNNNN

Where:
    GV       - fixed prefix identifying GramVaani AI
    YYYYMMDD - the date the complaint was generated (local date)
    NNNNN    - 5 random digits (zero-padded), e.g. "00001", "47213"

Example: GV-20260713-00001

This is entirely offline / local:
    - No external API calls of any kind.
    - No network access required.
    - Uses only Python's standard library (`datetime`, `random`).

This module is intentionally framework-agnostic (no Streamlit
imports) and does not depend on `ai/llm/complaint_generator.py` in
any way, so it can be called independently to attach an ID to a
complaint after it has been generated - without touching the
complaint generation logic itself.

Public API:
    generate_complaint_id() -> str
"""

import logging
import random
from datetime import date

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
# A dedicated, namespaced logger, consistent with the rest of the
# `ai` package (see ai/llm/complaint_generator.py, ai/schemes/
# scheme_recommender.py).
logger = logging.getLogger("gramvaani.ai.utils.complaint_id")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------
# Format configuration
# ----------------------------------------------------------------------
_ID_PREFIX: str = "GV"
_RANDOM_DIGIT_COUNT: int = 5
_RANDOM_DIGIT_MAX: int = (10 ** _RANDOM_DIGIT_COUNT) - 1  # 99999 for 5 digits


def generate_complaint_id() -> str:
    """
    Generates a new Complaint ID in the format GV-YYYYMMDD-NNNNN,
    using today's local date and 5 random digits.

    Returns:
        A Complaint ID string, e.g. "GV-20260713-00001".
    """
    date_part = date.today().strftime("%Y%m%d")
    random_part = str(random.randint(0, _RANDOM_DIGIT_MAX)).zfill(
        _RANDOM_DIGIT_COUNT
    )

    complaint_id = f"{_ID_PREFIX}-{date_part}-{random_part}"

    logger.info("Generated Complaint ID: %s", complaint_id)
    return complaint_id
