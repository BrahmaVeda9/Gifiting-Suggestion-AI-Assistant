import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GEMINI_API_KEY", "dummy_key"))
MODEL = "llama-3.3-70b-versatile"

def generate_why_note(recipient_name: str, strategy: str, gift: str, context: dict) -> str:
    """Uses Gemini to generate the heartfelt 'Why' Note."""

    
    frustrations = ", ".join(context.get("frustrations", []))
    
    prompt = f"""
    Write a short, heartfelt note to {recipient_name} to accompany their gift: {gift}.
    The strategy behind this gift is: {strategy}.
    This gift specifically addresses these daily annoyances they face: {frustrations}.
    
    The note should NOT sound like an AI wrote it. It should sound like a supportive friend/partner.
    Keep it under 4 sentences. Explain the thoughtful reason behind the gift.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Hey {recipient_name}, I saw this and thought of you. Hope it helps with your daily routine!"
