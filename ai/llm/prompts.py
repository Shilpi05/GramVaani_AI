"""
prompts.py
-----------
Prompt template(s) used by `complaint_generator.py` to instruct Gemini
to convert a raw citizen complaint transcript into a structured,
professional complaint record.

Kept separate from `complaint_generator.py` so the prompt wording can
be iterated on independently of the API-calling logic.
"""

# The exact JSON structure Gemini must return - shown to the model
# as a schema hint, and also used by complaint_generator.py to
# validate the parsed response.
COMPLAINT_JSON_SCHEMA_HINT: str = """{
  "complaint_type": "",
  "department": "",
  "priority": "",
  "summary": "",
  "formal_complaint": ""
}"""


def build_complaint_prompt(transcript: str) -> str:
    """
    Builds the full prompt sent to Gemini for complaint generation.

    Args:
        transcript: The citizen's complaint, transcribed from speech
            by `ai/speech/speech_service.py`.

    Returns:
        A complete prompt string instructing Gemini to analyze the
        transcript and return ONLY a JSON object matching the
        expected schema - no markdown, no extra commentary.
    """
    return f"""You are a civic governance assistant for GramVaani AI, a public
grievance redressal platform in India. A citizen has spoken a complaint,
which was transcribed by speech recognition. Your job is to convert this
raw transcript into a structured, professional complaint record.

Analyze the transcript and:
1. Identify the complaint category (e.g. "Road Damage", "Water Supply",
   "Electricity", "Sanitation", "Public Safety", "Corruption", "Other").
2. Identify the government department most likely responsible for
   resolving this issue (e.g. "Municipal Corporation", "Public Works
   Department", "Electricity Board", "Water Board", "Police Department").
3. Estimate a priority level: "High", "Medium", or "Low", based on the
   urgency and potential harm to public safety described.
4. Write a concise, neutral summary of the issue (1-2 sentences).
5. Write a formal, professional complaint letter body (3-5 sentences)
   suitable for submission to a government office, based strictly on
   what the citizen said. Do not invent facts not present in the
   transcript.

Citizen's transcript:
\"\"\"
{transcript}
\"\"\"

Respond with ONLY a valid JSON object and nothing else - no markdown
code fences, no explanations, no extra text before or after the JSON.
The JSON object must exactly match this structure:

{COMPLAINT_JSON_SCHEMA_HINT}
"""
