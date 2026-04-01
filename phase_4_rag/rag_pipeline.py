import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GEMINI_API_KEY", "dummy_key"))
MODEL = "llama-3.3-70b-versatile"

def get_strategy_cards(user_context: dict) -> list[dict]:
    """
    Uses Groq/Llama to generate 3 deeply personalised gifting strategy cards
    based on the user's extracted context (budget, preference_type, frustrations).
    Falls back to sensible defaults if the API call fails.
    """
    budget = user_context.get("budget", "unspecified")
    preference = user_context.get("preference_type", "thoughtful")
    frustrations = ", ".join(user_context.get("frustrations", []))
    relationship = user_context.get("has_relationship_context", False)

    prompt = f"""
You are Dearly, an expert AI gifting strategist. Based on the recipient profile below, generate exactly 3 gifting strategy cards.

Recipient Profile:
- Budget: {budget}
- Gift preference style: {preference} (utility = practical/daily use, wow = spectacular surprise)
- Daily frustrations/annoyances: {frustrations}
- Giver knows the relationship well: {relationship}

Return ONLY valid JSON — an array of exactly 3 objects. Each object must have:
- "name": A short, catchy strategy name (4-6 words max)
- "description": A 1-2 sentence description of the strategy
- "example_gift": A concrete example gift idea that fits this strategy and the given budget

Example format:
[
  {{
    "name": "The Morning Routine Fix",
    "description": "Target the chaotic morning rush by gifting something that saves time or reduces stress before 9am.",
    "example_gift": "A smart alarm clock with sunrise simulation ($45)"
  }}
]

Return ONLY the JSON array — no preamble, no explanation.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        text = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].strip()

        cards = json.loads(text)
        return cards if isinstance(cards, list) else []

    except Exception as e:
        print(f"[rag_pipeline] Error generating strategies: {e}")
        # Intelligent fallback cards
        return [
            {
                "name": "The Morning Routine Fix",
                "description": "Gifts that eliminate friction from the morning rush hour.",
                "example_gift": "Smart alarm clock with sunrise simulation"
            },
            {
                "name": "The Cozy Evening",
                "description": "Help them unwind and recharge after a long, draining day.",
                "example_gift": "Aromatherapy diffuser and essential oils set"
            },
            {
                "name": "The Commuter Buddy",
                "description": "Make their daily commute easier, faster, or more enjoyable.",
                "example_gift": "Noise-cancelling earbuds or a premium travel mug"
            }
        ]
