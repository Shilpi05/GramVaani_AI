# ai/speech

## Purpose
Handles speech-to-text (and eventually text-to-speech) for citizen
voice complaints, supporting multiple Indian languages/dialects so
citizens can speak naturally instead of typing.

## Expected Input
- Raw audio file or byte stream (e.g. `.wav`, `.mp3`, `.ogg`) captured
  from the "Voice Complaint" recorder on the File Complaint page.
- Optional language hint (e.g. `hi`, `en`, `bho`) if known.

## Expected Output
- Transcribed text of the complaint.
- Detected/confirmed language code.
- Confidence score for the transcription.

## Future Integration
Will be called from `frontend/pages/file_complaint.py` once the voice
recorder widget is implemented, and its output will be passed to
`backend/services` for storage alongside the complaint record.

No implementation exists yet.
