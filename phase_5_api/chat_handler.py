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

SYSTEM_PROMPT = """You are Dearly, a boutique AI gifting strategist. Your goal is to move from "Sense" (intake) to "Think" (strategies) as efficiently as possible.

=== INTAKE CRITERIA (CRITICAL) ===
You must have exactly 3 things to suggest strategies:
1. WHO & OCCASION (e.g., Mom's Birthday)
2. BUDGET (₹)
3. PASSION or CHALLENGE (e.g., Loves cooking)

=== THE GOAL ===
- If you HAVE all 3, you MUST output 'gift_ideas' immediately.
- If you are MISSING any, you MUST output 'conversation' and ask for ONLY what is missing.
- NEVER repeat facts the user already told you.
- NEVER output raw text outside the JSON block.

=== OUTPUT FORMAT (JSON ONLY) ===

Type 1: Conversation (Missing info)
{
  "type": "conversation",
  "message": "Warm, concise question about missing details."
}

Type 2: Strategies (Found info)
{
  "type": "gift_ideas",
  "message": "Warm intro to your strategies",
  "ideas": [
    {
      "strategy_name": "Catchy Theme",
      "reasoning": "Why this fits their context",
      "example_gift": "Concrete implementation",
      "confidence_score": 95
    }
  ]
}
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

def _extract_json(text: str) -> dict:
    """Robustly extracts and parses JSON from text, handling markdown fences and chatter."""
    try:
        # 1. Try direct parse
        return json.loads(text)
    except:
        # 2. Try re-finding the largest { } block
        try:
            match = re.search(r'(\{.*\})', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except:
            # 3. Last resort fallback
            return {"type": "conversation", "message": "I'm focusing so hard on the perfect gift that my thoughts got a little tangled! Could we try that again?"}

def chat(session_id: str, user_message: str, location: str = None, is_regeneration: bool = False) -> dict:
    session = get_session(session_id)
    if is_regeneration:
        if session["regeneration_count"] >= MAX_FREE_REGENERATIONS:
            return {"type": "paywall", "message": "Upgrade to Dearly Premium for unlimited concepts."}
        session["regeneration_count"] += 1
        session["history"].append({"role": "user", "content": "Provide 3 DIFFERENT strategies now."})
    else:
        session["history"].append({"role": "user", "content": user_message})

    # Prepare Context Memory
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if session.get("context"):
        ctx_str = json.dumps(session["context"])
        messages.append({"role": "system", "content": f"MEMORY: We already know this about the user: {ctx_str}. Do NOT ask for these again."})
    
    messages.extend(session["history"])

    global client
    if client is None: client = _get_client()

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.7)
        raw = response.choices[0].message.content.strip()
        result = _extract_json(raw)

        # Persistence logic
        session["history"].append({"role": "assistant", "content": json.dumps(result)})
        if result.get("type") == "gift_ideas" and result.get("ideas"):
            session["ideas"] = result["ideas"]
        
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
