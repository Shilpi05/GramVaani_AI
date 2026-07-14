"""
scheme_recommender.py
-----------------------
Government Scheme Recommendation service for GramVaani AI.

Given a generated complaint's `complaint_type`, `department`, and
`summary`, this module suggests 3-5 relevant Indian government
schemes that a citizen filing this complaint may also want to know
about (e.g. a "Water Supply" complaint might also surface schemes
like the Jal Jeevan Mission).

This is entirely offline / local:
    - No external API calls of any kind.
    - No network access required.
    - The knowledge base is a plain Python dictionary defined in this
      file, keyed by complaint category.

Matching strategy:
    The complaint's `complaint_type`, `department`, and `summary` are
    combined into a single lowercase string and checked against an
    ordered list of (category, keyword) rules. The first category
    whose keywords appear in the combined text wins. Ordering matters
    - more specific categories (e.g. "Street Lights", "Sewage",
    "Drainage") are checked before broader ones (e.g. "Water Supply",
    "Sanitation") so that, for example, a complaint mentioning
    "waterlogging" is correctly routed to Drainage rather than Water
    Supply.

Public API:
    recommend_schemes(complaint_type, department, summary)
        -> List[Dict[str, str]] | str

    Returns a list of 3-5 scheme dicts on a match, each shaped like:
        {
            "name": "...",
            "description": "...",
            "eligibility": "...",
            "official_department": "...",
        }

    If no category matches, returns the literal string
    "No direct government scheme found." instead of a list, so
    callers must check the return type before iterating.

This module is intentionally framework-agnostic (no Streamlit
imports) so it can be reused outside the UI later - e.g. from
`backend/services` or a future API layer - without modification.
"""

import logging
from typing import Dict, List, Union

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
# A dedicated, namespaced logger, consistent with the rest of the
# `ai` package (see ai/llm/complaint_generator.py).
logger = logging.getLogger("gramvaani.ai.schemes.scheme_recommender")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------
# Fallback message returned when no category matches.
# ----------------------------------------------------------------------
NO_SCHEME_FOUND_MESSAGE: str = "No direct government scheme found."

# ----------------------------------------------------------------------
# Local knowledge base: category -> 3-5 relevant government schemes.
# ----------------------------------------------------------------------
SCHEME_KNOWLEDGE_BASE: Dict[str, List[Dict[str, str]]] = {
    "Sanitation": [
        {
            "name": "Swachh Bharat Mission (Urban) 2.0",
            "description": (
                "A national mission focused on garbage-free cities, "
                "door-to-door waste collection, source segregation, "
                "and scientific processing of solid waste."
            ),
            "eligibility": (
                "All urban local body residents; municipal wards and "
                "households are covered through their local urban body."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
        {
            "name": "Swachh Bharat Mission (Gramin) Phase II",
            "description": (
                "Aims to sustain open-defecation-free status in villages "
                "and improve solid and liquid waste management in rural "
                "areas."
            ),
            "eligibility": (
                "Residents of rural areas and Gram Panchayats; "
                "implemented through village-level sanitation committees."
            ),
            "official_department": "Ministry of Jal Shakti",
        },
        {
            "name": "Namami Gange - Solid Waste Management Component",
            "description": (
                "Supports solid waste management infrastructure in towns "
                "along the Ganga river basin to reduce waste entering "
                "waterways."
            ),
            "eligibility": (
                "Residents of towns and cities located along the Ganga "
                "and its tributaries."
            ),
            "official_department": "Ministry of Jal Shakti",
        },
    ],
    "Water Supply": [
        {
            "name": "Jal Jeevan Mission",
            "description": (
                "Aims to provide functional household tap connections "
                "with adequate, safe drinking water to every rural "
                "household."
            ),
            "eligibility": (
                "Rural households without a functional tap water "
                "connection; applied for through the local Gram "
                "Panchayat or Village Water and Sanitation Committee."
            ),
            "official_department": "Ministry of Jal Shakti",
        },
        {
            "name": "AMRUT 2.0 (Water Supply Component)",
            "description": (
                "Focuses on universal coverage of water supply in urban "
                "areas through pipelines, storage, and distribution "
                "network upgrades."
            ),
            "eligibility": (
                "Residents of statutory towns and cities covered under "
                "the mission; administered through the urban local body."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
        {
            "name": "National Rural Drinking Water Programme",
            "description": (
                "Provides funding support to states for rural "
                "drinking-water infrastructure, including handpumps, "
                "piped supply schemes, and water quality monitoring."
            ),
            "eligibility": (
                "Rural habitations with inadequate or no safe drinking "
                "water source."
            ),
            "official_department": "Ministry of Jal Shakti",
        },
    ],
    "Roads": [
        {
            "name": "Pradhan Mantri Gram Sadak Yojana (PMGSY)",
            "description": (
                "Provides all-weather road connectivity to unconnected "
                "rural habitations, and upgrades existing rural roads."
            ),
            "eligibility": (
                "Unconnected rural habitations above the population "
                "threshold set for the state; requested through the "
                "Gram Panchayat or block office."
            ),
            "official_department": "Ministry of Rural Development",
        },
        {
            "name": "AMRUT 2.0 (Urban Roads Component)",
            "description": (
                "Supports road and footpath improvement, repair of "
                "potholes, and streetscape upgrades in mission cities."
            ),
            "eligibility": (
                "Residents of statutory towns and cities covered under "
                "the mission; administered through the urban local body."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
        {
            "name": "Central Road Fund Scheme",
            "description": (
                "Finances construction, maintenance, and repair of "
                "state and rural roads using a dedicated cess on fuel."
            ),
            "eligibility": (
                "State governments and local bodies applying on behalf "
                "of a stretch of road requiring repair or upgrade."
            ),
            "official_department": "Ministry of Road Transport and Highways",
        },
    ],
    "Electricity": [
        {
            "name": "Pradhan Mantri Sahaj Bijli Har Ghar Yojana (Saubhagya)",
            "description": (
                "Aims to achieve universal household electrification by "
                "providing last-mile electricity connections to willing "
                "un-electrified households."
            ),
            "eligibility": (
                "Un-electrified households, with free connections for "
                "households identified as poor under census data."
            ),
            "official_department": "Ministry of Power",
        },
        {
            "name": "Deen Dayal Upadhyaya Gram Jyoti Yojana (DDUGJY)",
            "description": (
                "Strengthens rural electricity distribution "
                "infrastructure, including feeder separation and "
                "metering, to improve power supply quality in villages."
            ),
            "eligibility": (
                "Rural households and agricultural consumers within "
                "areas covered by the state distribution utility."
            ),
            "official_department": "Ministry of Power",
        },
        {
            "name": "Revamped Distribution Sector Scheme (RDSS)",
            "description": (
                "Funds upgrades to distribution transformers, feeders, "
                "and smart metering to reduce outages and improve "
                "supply reliability."
            ),
            "eligibility": (
                "Consumers served by a participating state electricity "
                "distribution company (DISCOM)."
            ),
            "official_department": "Ministry of Power",
        },
    ],
    "Sewage": [
        {
            "name": "AMRUT 2.0 (Sewerage and Septage Management)",
            "description": (
                "Funds sewerage network expansion, sewage treatment "
                "plants, and septage management to ensure safe "
                "wastewater disposal in cities."
            ),
            "eligibility": (
                "Residents of statutory towns and cities covered under "
                "the mission; administered through the urban local body."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
        {
            "name": "Namami Gange - Sewage Infrastructure Component",
            "description": (
                "Builds and upgrades sewage treatment infrastructure in "
                "towns along the Ganga basin to prevent untreated "
                "sewage from entering the river."
            ),
            "eligibility": (
                "Residents of towns and cities located along the Ganga "
                "and its tributaries."
            ),
            "official_department": "Ministry of Jal Shakti",
        },
        {
            "name": "Swachh Bharat Mission (Urban) 2.0 - Faecal Sludge Management",
            "description": (
                "Supports safe collection, transport, and treatment of "
                "faecal sludge and septage in towns without full "
                "underground sewerage networks."
            ),
            "eligibility": (
                "All urban local body residents, especially in areas "
                "not yet covered by piped sewerage."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
    ],
    "Street Lights": [
        {
            "name": "Street Lighting National Programme (SLNP)",
            "description": (
                "Replaces conventional street lights with energy-"
                "efficient LED fixtures at no upfront cost to municipal "
                "bodies, funded through resulting energy savings."
            ),
            "eligibility": (
                "Municipalities and urban local bodies; individual "
                "outage complaints are routed to the local body for "
                "repair under the programme."
            ),
            "official_department": "Ministry of Power",
        },
        {
            "name": "AMRUT 2.0 (Urban Infrastructure - Street Lighting)",
            "description": (
                "Covers installation and maintenance of street lighting "
                "as part of broader urban infrastructure upgrades in "
                "mission cities."
            ),
            "eligibility": (
                "Residents of statutory towns and cities covered under "
                "the mission; administered through the urban local body."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
        {
            "name": "Finance Commission Grants to Local Bodies",
            "description": (
                "Untied grants to Panchayats and municipalities that "
                "can be used, among other things, for street lighting "
                "repair and maintenance in the local area."
            ),
            "eligibility": (
                "Residents of the Panchayat or municipal ward covered "
                "by the grant; raised through the local body."
            ),
            "official_department": "Ministry of Panchayati Raj / Ministry of Housing and Urban Affairs",
        },
    ],
    "Public Health": [
        {
            "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
            "description": (
                "Provides health insurance cover for hospitalization "
                "expenses to economically vulnerable families at "
                "empanelled hospitals."
            ),
            "eligibility": (
                "Families identified as economically vulnerable under "
                "the Socio-Economic Caste Census (SECC) database."
            ),
            "official_department": "Ministry of Health and Family Welfare",
        },
        {
            "name": "National Health Mission (NHM)",
            "description": (
                "Strengthens public health infrastructure, disease "
                "surveillance, and community health worker outreach in "
                "both rural and urban areas."
            ),
            "eligibility": (
                "All residents accessing public health facilities such "
                "as Primary Health Centres and Community Health Centres."
            ),
            "official_department": "Ministry of Health and Family Welfare",
        },
        {
            "name": "Ayushman Bharat Health and Wellness Centres",
            "description": (
                "Provides free essential drugs, diagnostics, and "
                "preventive/promotive primary healthcare services close "
                "to citizens' homes."
            ),
            "eligibility": (
                "All residents within the catchment area of a "
                "designated Health and Wellness Centre."
            ),
            "official_department": "Ministry of Health and Family Welfare",
        },
    ],
    "Drainage": [
        {
            "name": "AMRUT 2.0 (Stormwater Drainage Component)",
            "description": (
                "Funds construction and desilting of stormwater drains "
                "to reduce urban waterlogging and flooding during "
                "monsoons."
            ),
            "eligibility": (
                "Residents of statutory towns and cities covered under "
                "the mission; administered through the urban local body."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
        {
            "name": "Flood Management and Border Areas Programme (FMBAP)",
            "description": (
                "Supports drainage improvement and flood-control "
                "infrastructure in flood-prone and waterlogging-prone "
                "areas."
            ),
            "eligibility": (
                "Residents of areas identified as flood-prone by the "
                "state government's flood management plan."
            ),
            "official_department": "Ministry of Jal Shakti",
        },
        {
            "name": "Swachh Bharat Mission (Urban) 2.0 - Drain Desilting",
            "description": (
                "Covers routine desilting and cleaning of local "
                "stormwater and sullage drains as part of citywide "
                "sanitation upkeep."
            ),
            "eligibility": (
                "All urban local body residents; requested through the "
                "local municipal ward office."
            ),
            "official_department": "Ministry of Housing and Urban Affairs",
        },
    ],
}

# ----------------------------------------------------------------------
# Keyword rules used to classify a complaint into one of the
# categories above. Order matters: more specific categories are
# checked first so overlapping words (e.g. "water") don't cause a
# complaint to be misrouted to a broader category.
# ----------------------------------------------------------------------
_CATEGORY_KEYWORD_RULES: List[tuple] = [
    (
        "Street Lights",
        [
            "street light",
            "streetlight",
            "street lamp",
            "lamp post",
            "lamppost",
            "street lighting",
        ],
    ),
    (
        "Sewage",
        ["sewage", "sewer", "manhole", "wastewater", "waste water"],
    ),
    (
        "Drainage",
        [
            "drainage",
            "drain",
            "waterlogging",
            "water logging",
            "flooding",
            "flood",
        ],
    ),
    (
        "Water Supply",
        [
            "water supply",
            "drinking water",
            "water pipeline",
            "water tanker",
            "water shortage",
            "no water",
            "water tank",
            "tap water",
        ],
    ),
    (
        "Electricity",
        [
            "electricity",
            "power cut",
            "power outage",
            "power supply",
            "transformer",
            "voltage",
            "electric pole",
            "power failure",
        ],
    ),
    (
        "Roads",
        ["road", "pothole", "highway", "footpath", "pavement"],
    ),
    (
        "Public Health",
        [
            "health",
            "hospital",
            "disease",
            "epidemic",
            "medical",
            "clinic",
            "outbreak",
        ],
    ),
    (
        "Sanitation",
        [
            "sanitation",
            "garbage",
            "waste",
            "trash",
            "cleanliness",
            "sweeping",
            "litter",
        ],
    ),
]


def _build_search_text(complaint_type: str, department: str, summary: str) -> str:
    """
    Combines the complaint's fields into a single lowercase string
    suitable for keyword matching.

    Args:
        complaint_type: The complaint category, as classified by the
            complaint generator (e.g. "Road Damage").
        department: The government department identified as
            responsible (e.g. "Public Works Department").
        summary: The 1-2 sentence complaint summary.

    Returns:
        A single lowercase string concatenating all three fields.
    """
    parts = [complaint_type or "", department or "", summary or ""]
    return " ".join(parts).lower()


def _match_category(search_text: str) -> str:
    """
    Finds the first category whose keywords appear in `search_text`.

    Args:
        search_text: Lowercase combined text built by
            `_build_search_text()`.

    Returns:
        The matched category name, or an empty string if none match.
    """
    for category, keywords in _CATEGORY_KEYWORD_RULES:
        for keyword in keywords:
            if keyword in search_text:
                return category
    return ""


def recommend_schemes(
    complaint_type: str, department: str, summary: str
) -> Union[List[Dict[str, str]], str]:
    """
    Recommends 3-5 relevant government schemes for a generated
    complaint, using only the local offline knowledge base defined in
    this module (no external API calls).

    Args:
        complaint_type: The complaint category (e.g. "Water Supply",
            "Road Damage").
        department: The government department identified as
            responsible for the complaint.
        summary: The 1-2 sentence complaint summary.

    Returns:
        A list of 3-5 scheme dicts, each with keys "name",
        "description", "eligibility", and "official_department", if a
        matching category is found.

        If no category matches, returns the literal string
        "No direct government scheme found." instead of a list.
        Callers must check the return type (list vs str) before
        iterating over the result.
    """
    search_text = _build_search_text(complaint_type, department, summary)
    matched_category = _match_category(search_text)

    if not matched_category:
        logger.warning(
            "No matching scheme category found for complaint_type=%r, "
            "department=%r.",
            complaint_type,
            department,
        )
        return NO_SCHEME_FOUND_MESSAGE

    schemes = SCHEME_KNOWLEDGE_BASE.get(matched_category, [])
    if not schemes:
        # Defensive fallback - should not happen since every category
        # in _CATEGORY_KEYWORD_RULES has a corresponding knowledge
        # base entry, but guards against future edits going out of
        # sync.
        logger.warning(
            "Matched category '%s' has no schemes defined in the "
            "knowledge base.",
            matched_category,
        )
        return NO_SCHEME_FOUND_MESSAGE

    logger.info(
        "Matched category '%s' for complaint_type=%r, department=%r - "
        "returning %d scheme(s).",
        matched_category,
        complaint_type,
        department,
        len(schemes),
    )
    return schemes
