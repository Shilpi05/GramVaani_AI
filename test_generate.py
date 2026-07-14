from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say only Hello"
)
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]

for model in MODELS:
    print("=" * 60)
    print(model)
    try:
        response = client.models.generate_content(
            model=model,
            contents="Reply with ONLY Hello."
        )
        print(response.text)
    except Exception as e:
        print(type(e).__name__, e)
print(response.text)