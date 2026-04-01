import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from groq import Groq

api_key = os.getenv("GEMINI_API_KEY", "")
print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")

client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'Groq API key is working!' and nothing else."}],
        max_tokens=20,
    )
    print("\n[SUCCESS] " + response.choices[0].message.content)
except Exception as e:
    print(f"\n[FAILED] {e}")
