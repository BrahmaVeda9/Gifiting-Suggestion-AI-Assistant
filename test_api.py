import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
print(f"Key identified: {key[:10]}...")

client = Groq(api_key=key)
try:
    models = client.models.list()
    print("Available Models:")
    for m in models.data:
        print(f"- {m.id}")
except Exception as e:
    print(f"FAILED to list models: {e}")
