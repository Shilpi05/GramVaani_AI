from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

print("Loaded key:", key)
print("Starts with:", key[:10])
print("Ends with:", key[-6:])