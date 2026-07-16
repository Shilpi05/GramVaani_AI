# ai/speech

## Purpose
Speech-to-text for citizen voice complaints, using OpenAI's Whisper
model, so citizens can speak naturally instead of typing.

## Files

- `speech_service.py` — loads and caches a Whisper model, and exposes
  `transcribe_audio(audio_path, language=None) -> str`. Language is
  optional; when omitted, Whisper auto-detects it.
- `speech_utils.py` — filesystem helpers used around the transcription
  call: `is_supported_extension()`, `save_uploaded_audio()` (writes a
  Streamlit `UploadedFile` to a temp path), and `delete_temp_file()`
  (cleanup after transcription).

## Expected Input
An audio file path (`.wav`, `.mp3`, `.m4a` - see `speech_utils.py`
for the exact supported-extension list) and an optional language
code.

## Expected Output
The transcribed text as a plain string.

## Configuration
Optional `WHISPER_MODEL` environment variable to choose model size
(`tiny`, `base`, `small`, `medium`, `large`); defaults to `small`.

## Used by
`frontend/pages/file_complaint.py`'s "Process Audio" button: the
citizen's uploaded audio is saved to a temp file, transcribed here,
and the temp file is deleted immediately after.
