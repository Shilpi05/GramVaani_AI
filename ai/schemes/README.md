# ai/schemes

## Purpose
Matches a generated complaint against a local knowledge base of
Indian government schemes, so a citizen filing a complaint also sees
relevant support programs (e.g. a "Water Supply" complaint surfaces
the Jal Jeevan Mission).

## Files

- `scheme_recommender.py` — exposes
  `recommend_schemes(complaint_type, department, summary)`. The
  knowledge base is a plain Python dict in this file, covering 8
  categories (Sanitation, Water Supply, Roads, Electricity, Sewage,
  Street Lights, Public Health, Drainage), each with 3 real schemes.
  Matching is keyword-based against the combined complaint text,
  checked in most-specific-first order so overlapping terms (e.g.
  "waterlogging") route to the right category.

## Expected Input
Three strings from a generated complaint: `complaint_type`,
`department`, `summary`.

## Expected Output
A list of 3-5 scheme dicts (`name`, `description`, `eligibility`,
`official_department`), or the literal string
`"No direct government scheme found."` if no category matches.

## Configuration
None - entirely offline, no external API calls, no environment
variables.

## Used by
`frontend/pages/file_complaint.py`, right after a complaint is
generated (schemes are computed there, since that's where the
complaint data lives) and displayed on
`frontend/pages/scheme_finder.py` (which reads the result from
`st.session_state` rather than recomputing it).
