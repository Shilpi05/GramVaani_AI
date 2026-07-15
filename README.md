# GramVaani AI

**One Voice. One Platform. Better Governance.**

An AI-powered, multilingual public governance platform for India.
Citizens will be able to file complaints by voice, upload issue
photos, discover government schemes, and track complaint status.

> **Current stage:** UI skeleton only. No AI, no backend logic, no
> external APIs are wired in yet. This repository is structured so
> those pieces can be added later without restructuring.

---

## 1. Project Overview

GramVaani AI aims to lower the barrier between citizens and public
services by letting people interact in their own language and voice,
rather than navigating complex government forms and portals.

Planned capabilities (not yet implemented):

| Module          | What it will do                                |
| --------------- | ---------------------------------------------- |
| File Complaint  | Voice + photo based complaint registration     |
| Scheme Finder   | Personalized government scheme recommendations |
| Track Complaint | Real-time complaint status tracking            |

---

## 2. Folder Structure

```
GRAMVAANI_AI/
├── app.py                        # Entry point - configuration + routing only
│
├── frontend/                     # Everything UI-related
│   ├── pages/                    # One file per screen, each exposing render()
│   │   ├── home.py
│   │   ├── file_complaint.py
│   │   ├── scheme_finder.py
│   │   ├── track_complaint.py
│   │   └── settings.py
│   ├── components/                # Reusable UI building blocks
│   │   ├── sidebar.py             # Navigation rendering
│   │   └── theme.py                # Colors, typography, spacing, CSS, helpers
│   ├── config/
│   │   └── constants.py           # ALL static text, labels, nav items, version
│   ├── utils/
│   │   └── helpers.py             # Shared stateless helper functions (future)
│   └── assets/
│       ├── logo/                  # Brand logo files (future)
│       └── icons/                 # Custom icon files (future)
│
├── ai/                            # Future AI modules (documentation only)
│   ├── speech/                    # Speech-to-text / text-to-speech
│   ├── vision/                    # Image classification for complaints
│   ├── translation/               # Multilingual translation
│   ├── llm/                       # Scheme recommendation, summarization
│   └── prompts/                   # Prompt template library
│
├── backend/                       # Future backend modules (documentation only)
│   ├── services/                  # Business logic layer
│   ├── database/                  # DB connection, schema, queries
│   ├── models/                    # Data models / schemas
│   └── api/                       # Optional HTTP API layer
│
├── data/                          # Future datasets (schemes, sample records)
├── docs/                          # Project documentation
├── uploads/                       # Future user-uploaded files (audio, images)
├── resources/                     # Misc supporting resources
├── requirements.txt
└── .env
```

---

## 3. Installation

```bash
git clone <repository-url>
cd GRAMVAANI_AI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4. Running the Project

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 5. Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        app.py                            │
│        (page config → theme → sidebar → routing)         │
└───────────────┬───────────────────────┬──────────────────┘
                │                       │
                ▼                       ▼
    ┌────────────────────┐   ┌───────────────────────┐
    │ frontend/components │   │   frontend/pages       │
    │  - sidebar.py        │   │   - home.py            │
    │  - theme.py           │  │   - file_complaint.py  │
    └──────────┬───────────┘   │   - scheme_finder.py   │
               │                │   - track_complaint.py │
               ▼                │   - settings.py        │
    ┌────────────────────┐     └───────────┬────────────┘
    │ frontend/config      │                 │
    │  - constants.py       │◄───────────────┘
    └────────────────────┘
               (all pages import text/labels from here)

    ── Not yet wired in ──────────────────────────────────
    frontend/pages/*  --->  backend/services  --->  backend/database
    frontend/pages/*  --->  ai/speech, ai/vision, ai/translation, ai/llm
```

---

## 6. Future Modules

- **`ai/speech`** — voice-to-text for complaint filing.
- **`ai/vision`** — image classification for uploaded complaint photos.
- **`ai/translation`** — multilingual UI/content translation.
- **`ai/llm`** — scheme recommendation and complaint summarization.
- **`ai/prompts`** — prompt templates consumed by `ai/llm`.
- **`backend/services`** — business logic orchestration.
- **`backend/database`** — persistence layer.
- **`backend/models`** — shared data models.
- **`backend/api`** — optional external HTTP API.

Each of the folders above currently contains only a `README.md`
describing its purpose, expected input/output, and how it will
eventually connect to the frontend - no implementation yet.

---

## 7. Contributing

1. Keep `app.py` thin — configuration and routing only.
2. New pages: add a file to `frontend/pages/` exposing a single
   `render()` function, then register it in `app.py`'s `PAGE_ROUTER`
   and in `NAV_ITEMS` inside `frontend/config/constants.py`.
3. Never hardcode user-facing text in a page file — add it to
   `frontend/config/constants.py` instead.
4. Never hardcode colors/spacing in a page file — use the helpers
   and CSS classes provided by `frontend/components/theme.py`.
5. Follow PEP8, include docstrings and type hints on all new
   functions.
