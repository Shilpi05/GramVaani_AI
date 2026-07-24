# GramVaani AI

**One Voice. One Platform. Better Governance.**

An AI-powered, bilingual (English/Hindi) civic complaint platform. A citizen
speaks a complaint in their own language; the app transcribes it, drafts a
formal grievance, matches it against relevant government schemes, and gives
the citizen a trackable Complaint ID — no login, no form-filling, no
database.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gramvaani-ai.streamlit.app/)

---

## Features

| Capability                     | How it works                                                                                                                                                                                                                            |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Voice-to-text**              | Citizen uploads a WAV/MP3/M4A recording; OpenAI **Whisper** transcribes it, with automatic language detection.                                                                                                                          |
| **AI complaint drafting**      | The transcript is sent to **Groq** (`llama-3.3-70b-versatile`, falling back to `llama-3.1-8b-instant`), which returns a structured complaint: type, responsible department, priority, summary, and a formal letter body.                |
| **Evidence photos**            | Citizen can attach a JPG/PNG photo (e.g. a pothole) alongside the voice complaint. Saved locally, previewed, size/type validated.                                                                                                       |
| **Government scheme matching** | The complaint is matched offline, via keyword rules, against a local knowledge base of 25 Indian government schemes across 8 categories (Sanitation, Water Supply, Roads, Electricity, Sewage, Street Lights, Public Health, Drainage). |
| **Complaint ID & PDF export**  | Every complaint gets a unique ID (`GV-YYYYMMDD-NNNNN`) and can be downloaded as a formatted PDF.                                                                                                                                        |
| **Status tracking**            | A citizen can look up a Complaint ID and see a progress timeline (Submitted → Under Review → Assigned → Resolved), priority, department, and an estimated resolution window.                                                            |
| **Settings**                   | Application language, preferred complaint language, auto-delete for uploaded files, and Clear Session / Restore Defaults.                                                                                                               |
| **Bilingual interface**        | The full interface, not just complaint content, is available in English and Hindi and switches instantly from Settings.                                                                                                                 |

Image classification (`ai/vision`) and speech translation (`ai/translation`)
are scoped but not yet implemented.

There is no database and no user accounts. Every complaint, scheme match,
and tracking record lives in `st.session_state` for the length of the
browser session.

---

## Tech stack

| Layer                | Technology                                                                  |
| -------------------- | --------------------------------------------------------------------------- |
| UI framework         | [Streamlit](https://streamlit.io)                                           |
| Speech-to-text       | [OpenAI Whisper](https://github.com/openai/whisper) (local inference)       |
| Complaint generation | [Groq](https://groq.com) API (Llama 3.3 / 3.1)                              |
| PDF generation       | [ReportLab](https://www.reportlab.com/)                                     |
| Scheme matching      | Local, offline keyword-rule engine                                          |
| State                | `st.session_state` only — no database                                       |
| Config               | `.env` (Groq key, model selection) + `.streamlit/config.toml` (fixed theme) |

---

## Project structure

```
GramVaani_AI/
├── app.py                          # Entry point - page config + routing only
│
├── frontend/
│   ├── pages/                      # One file per screen, each exposing render()
│   │   ├── home.py
│   │   ├── file_complaint.py       # Voice + evidence upload + AI drafting
│   │   ├── scheme_finder.py        # Displays schemes matched during complaint generation
│   │   ├── track_complaint.py      # Complaint ID lookup + status timeline
│   │   └── settings.py             # Language, preferences, session controls
│   ├── components/
│   │   ├── sidebar.py              # Navigation (bilingual via i18n)
│   │   ├── theme.py                # Design tokens, global CSS, shared UI helpers
│   │   └── evidence_uploader.py    # Reusable photo-upload widget
│   ├── config/
│   │   └── constants.py            # Static, non-translatable config (nav structure, defaults)
│   └── utils/
│       ├── i18n.py                 # Centralized EN/HI translation table + t() helper
│       └── helpers.py              # Shared stateless helpers (e.g. page navigation)
│
├── ai/                              # Framework-agnostic business logic (no Streamlit imports)
│   ├── speech/                      # Whisper transcription
│   ├── llm/                         # Groq complaint generation
│   ├── schemes/                     # Offline scheme matching
│   ├── utils/                       # Complaint ID, PDF export, mock tracking
│   ├── vision/                      # Image classification - planned
│   ├── translation/                 # Speech translation - planned
│   └── prompts/                     # Shared prompt library - planned
│
├── requirements.txt
├── .env.example
└── .streamlit/config.toml           # Pinned light theme (brand colors)
```

Pages never call Groq or Whisper directly — they call into `ai/`, which has
no knowledge that Streamlit exists.

---

## Architecture

```
Citizen's voice
     │
     ▼
Whisper (ai/speech)        →  transcript
     │
     ▼
Groq LLM (ai/llm)           →  structured complaint (type, department,
     │                          priority, summary, formal text)
     ▼
ai/utils                    →  Complaint ID, PDF, tracking status
ai/schemes                  →  matched government schemes
     │
     ▼
st.session_state            →  read back by whichever page the citizen
                                navigates to next
```

The frontend (`frontend/pages`, `components`, `utils/i18n.py`) only handles
UI, routing, and translation. All business logic lives in `ai/`, and `ai/`
has no dependency on Streamlit.

---

## Setup

```bash
git clone <repository-url>
cd GramVaani_AI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq API key to `.env`:

```
GROQ_API_KEY=your_groq_api_key_here
```

Optional overrides in `.env.example`: model selection, Whisper model size,
request timeout/retries.

## Running

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## Contributing

- Keep `app.py` thin — configuration and routing only.
- New pages: add a file to `frontend/pages/` with a single `render()`
  function, then register it in `app.py`'s `PAGE_ROUTER` and in
  `NAV_ITEMS` in `frontend/config/constants.py`.
- All interface text goes through `t("key")` from `frontend/utils/i18n.py`,
  with both an `en` and `hi` entry. This doesn't apply to AI-generated
  complaint content, scheme names, or department names — those are data,
  not interface copy.
- Business logic belongs in `ai/`, not in a page file.
- Use the tokens and CSS classes in `frontend/components/theme.py` rather
  than hardcoding colors or spacing.
- Follow PEP8; include docstrings and type hints on new functions.
