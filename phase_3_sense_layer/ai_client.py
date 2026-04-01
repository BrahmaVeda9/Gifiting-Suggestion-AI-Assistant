import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GEMINI_API_KEY", "dummy_key"))
MODEL = "llama-3.3-70b-versatile"

def extract_gifting_context(chat_history: str) -> dict:
    """Uses Gemini to parse user's unstructured input into structured variables constrainting the gift search."""

    
    prompt = f"""
    You are an expert AI gifting assistant named Dearly. Based on the following chat history with a user, extract the key constraints.
    1. The budget (if mentioned, otherwise null).
    2. Preference type ("wow" or "utility" - if mentioned, otherwise null. "utility" means they prefer something useful for daily life, "wow" means they want a spectacular surprise).
    3. A list of daily annoyances or frustrations they mentioned about the recipient.
    4. Whether they provided context about their relationship (true/false).
    
    Return ONLY valid JSON with keys: "budget", "preference_type", "frustrations", "has_relationship_context".
    
    Chat History:
    {chat_history}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        text = response.choices[0].message.content
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1]
            if text.startswith("json\n"):
                text = text[5:]
        return json.loads(text.strip())
    except Exception as e:
        return {
            "budget": None,
            "preference_type": None,
            "frustrations": [],
            "has_relationship_context": False,
            "error": str(e)
        }
