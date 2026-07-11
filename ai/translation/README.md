# ai/translation

## Purpose
Provides multilingual support across the platform by translating
complaint text, scheme descriptions, and UI content between English
and regional Indian languages.

## Expected Input
- Source text string.
- Source language code (or "auto" for detection).
- Target language code.

## Expected Output
- Translated text string.
- Detected source language (if auto-detected).

## Future Integration
Will sit between `ai/speech` (transcribed text) and `backend/services`
(storage), and will also be used by `frontend/pages/scheme_finder.py`
to present scheme information in the citizen's preferred language.

No implementation exists yet.
