import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
MODEL = "llama-3.1-8b-instant"

def _get_client():
    # 1. Try Streamlit Secrets (Cloud Deployment)
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return Groq(api_key=st.secrets["GROQ_API_KEY"])
        if "GEMINI_API_KEY" in st.secrets:
            return Groq(api_key=st.secrets["GEMINI_API_KEY"])
    except:
        pass

    # 2. Try OS Environment (Local Development)
    key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not key or key == "dummy_key":
        # Check standard locations or common mistakes
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not key:
        raise ValueError("No API Key found. Please set GROQ_API_KEY in Streamlit Secrets or .env")
        
    return Groq(api_key=key)

client = None # initialized on first use

# In-memory session store: {session_id: {"history": [], "context": {}, "ideas": [], "regeneration_count": 0}}
sessions = {}

# We simulate a paywall after they ask for "Alternative Ideas" more than once.
MAX_FREE_REGENERATIONS = 1

SYSTEM_PROMPT = """You are Dearly, an extremely intelligent and empathetic AI gifting strategist.
Your purpose is to move from "Sense" (gathering context) to "Think" (generating strategies) as efficiently as possible.

=== INTAKE LOGIC (CRITICAL) ===
- You need exactly 3 things to suggest strategies: (1) WHO/OCCASION, (2) BUDGET (₹), (3) at least ONE PASSION/CHALLENGE.
- If the user provides all 3 in their first message, you MUST jump to "gift_ideas" immediately. Do NOT ask follow-up questions.
- NEVER repeat information the user has already given (e.g., "I see you mentioned..."). Move straight to the *next* logical step.
- Be concise. Aims for a 2-turn maximum for intake.

=== STRATEGY-FIRST OUTPUT ===
- Suggest exactly 3 Gifting Strategies.
- strategy_name: Catchy theme (e.g., "The Morning Routine Fix")
- reasoning: Connecting the strategy to their specific passion/frustration.
- example_gift: The concrete implementation.
- confidence_score: 1-100.

=== OUTPUT FORMAT ===
You ONLY output valid JSON. No preamble. No conversational text outside the JSON.

Type 1: Conversation (Still gathering info)
{"type": "conversation", "message": "Warm, combined question about missing info."}

Type 2: Strategies (When you have Occasion, Budget, and Passion)
{"type": "gift_ideas", "message": "Warm intro to your strategies", "ideas": [...]}
"""

def get_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "context": {},
            "ideas": [],
            "regeneration_count": 0
        }
    return sessions[session_id]

def chat(session_id: str, user_message: str, location: str = None, is_regeneration: bool = False) -> dict:
    session = get_session(session_id)

    if location and location.strip():
        session["context"]["location"] = location.strip()

    if is_regeneration:
        if session["regeneration_count"] >= MAX_FREE_REGENERATIONS:
            return {"type": "paywall", "message": "Upgrade to Dearly Premium for unlimited strategy concepts."}
        session["regeneration_count"] += 1
        session["history"].append({"role": "user", "content": "Provide 3 DIFFERENT strategies now."})
    else:
        session["history"].append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(session["history"])

    global client
    if client is None:
        client = _get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7
        )
        raw = response.choices[0].message.content.strip()

        # Robust JSON extraction: Find the LAST JSON block in case the LLM leaked text
        json_blocks = re.findall(r'\{.*\}', raw, re.DOTALL)
        if json_blocks:
            raw_json = json_blocks[-1]
        else:
            raw_json = raw

        try:
             result = json.loads(raw_json)
             if not isinstance(result, dict):
                 result = {"type": "conversation", "message": str(result)}
        except:
             # Fallback extraction if JSON has common minor errors
             result = {"type": "conversation", "message": "I'm having a little trouble structuring my thoughts! Could we try that again?"}

        session["history"].append({"role": "assistant", "content": json.dumps(result)})

        if result.get("type") == "gift_ideas" and result.get("ideas"):
            session["ideas"] = result["ideas"]
            if result.get("occasion"):
                 session["context"]["occasion"] = result["occasion"]

        if not is_regeneration:
             _extract_context(session, user_message)

        return result

    except Exception as e:
        return {"type": "error", "message": "I hit a small bump in my gifting logic. Let's try again!"}

def generate_note_for_idea(session_id: str, idea_title: str, idea_reasoning: str, recipient_name: str = "them") -> dict:
    session = get_session(session_id)
    
    history_text = " ".join(
        m["content"] for m in session["history"] if m["role"] == "user"
    )

    prompt = f"""Write a beautiful, heartfelt note to accompany this gift concept for {recipient_name}.

Gift concept: {idea_title}
Context for why this was chosen: {idea_reasoning}
What the user told us about them: {history_text[:800]}

Rules:
- Sound like a genuinely thoughtful person giving a gift. Warm, emotional, natural.
- Keep it to 3-4 sentences max.
- DON'T explicitly name a brand or product. Reference the *feeling* and the *concept*.
- NO generic openings like "Dear [Name]" or "Sincerely". Just jump into the feelings.
- ONLY output the note text.
"""

    global client
    if client is None:
        client = _get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=250,
        )
        note_text = response.choices[0].message.content.strip()
        note_text = note_text.strip('"').strip("'")
        return {"type": "note", "note": note_text}
    except Exception as e:
        return {"type": "note", "note": "I saw this and immediately thought of you — I hope it brings a little extra joy to your days."}

def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]

def _extract_context(session: dict, user_message: str):
    msg_lower = user_message.lower()

    # Budget
    if "budget" not in session["context"]:
        # Prioritize Indian Rupees, then other currencies, then plain numbers as Rupees
        patterns = [
            r'₹\s*[\d,]+', r'inr\s*[\d,]+', r'[\d,]+\s*rupees?',
            r'\$\s*[\d,]+', r'£\s*[\d,]+', r'€\s*[\d,]+',
            r'[\d,]+\s*(dollars?|usd|pounds?|euros?|bucks?|k\b)',
            r'(budget|around|under|about)\s+(?:of\s+)?(?:rs\.?\s+)?([\d,]+)'
        ]
        for pat in patterns:
            m = re.search(pat, msg_lower)
            if m:
                val = m.group()
                # If it's a plain group match from the last pattern, prepend ₹
                if pat == patterns[-1]:
                    val = f"₹{m.group(2)}"
                session["context"]["budget"] = val
                break

    # Relationship
    if "relationship" not in session["context"]:
        for rel in ["wife", "husband", "partner", "girlfriend", "boyfriend", "mom", "dad", "mother", "father", "sister", "brother", "friend", "colleague", "boss", "fiance", "fiancée"]:
            if re.search(r'\b' + rel + r'\b', msg_lower):
                session["context"]["relationship"] = rel
                break
