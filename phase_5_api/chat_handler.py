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

SYSTEM_PROMPT = """You are Dearly, an incredibly warm, empathetic, and emotionally intelligent AI gifting strategist. You speak like a thoughtful friend who genuinely cares about making people feel special.
Your SOLE purpose is to help users find deeply meaningful **Gifting Strategies** — high-level frameworks (e.g., "The Morning Routine Fix") that solve a specific "pain point" or celebrate a specific "passion".

=== STRATEGY-FIRST Gifting (CRITICAL) ===
- You do NOT jump straight to products or basic gift ideas.
- Each suggestion must be a **Strategy** with a catchy, thematic name.
- A Strategy is the *Framework* (the "Why") and the **Example Gift** is the *Implementation* (the "What").
- EXAMPLE:
    - Strategy Name: "The Heritage Curator"
    - Reasoning: "Because she loves her family history, this strategy focuses on preserving legacies..."
    - Example Gift: "A custom hand-bound leather binder for her recipe notes."

=== EMPATHY & TONE (CRITICAL) ===
- Respond with genuine warmth and curiosity.
- Acknowledge the user's situation briefly based ONLY on facts they provided.
- NEVER assume relationship status or living situations.
- NEVER sound robotic or interrogative.

=== STRICT GUARDRAILS ===
- You ONLY handle gift-related conversations. If unrelated, respond with type "guardrail".
- NEVER mention specific brand names, retailers, apps, or product names.
- NEVER suggest a product as the strategy itself (e.g., NO "Apple Watch").
- ONLY suggest Gifting STRATEGIES (Themes) with one supporting Example Gift.
- CURRENCY: Always assume and use Indian Rupees (₹) for all budget mentions. Treat plain numbers as ₹.

=== HOW TO GATHER INFORMATION ===
Do NOT suggests strategies until you have:
1. WHO & OCCASION
2. BUDGET in Rupees (₹)
3. PASSIONS/CHALLENGES (At least one)

Rules for asking questions:
- Aims for exactly 2-3 conversational turns before generating ideas.
- COMBINE questions naturally.
- Once you have the core details, STOP and output 3 Strategic Suggestions.

=== OUTPUT FORMAT ===
You MUST respond in ONLY valid JSON. 

When ready to present 3 Suggestions:
{
  "type": "gift_ideas",
  "occasion": "Occasion name",
  "message": "Your warm intro",
  "ideas": [
    {
      "strategy_name": "Catchy Theme Name",
      "reasoning": "Explanation connecting strategy to user context",
      "example_gift": "A concrete implementation/gift idea",
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

def chat(session_id: str, user_message: str, location: str = None, is_regeneration: bool = False) -> dict:
    session = get_session(session_id)

    if location and location.strip():
        session["context"]["location"] = location.strip()

    if is_regeneration:
        # Check paywall limits
        if session["regeneration_count"] >= MAX_FREE_REGENERATIONS:
            return {
                "type": "paywall",
                "message": "You've reached the limit of free idea regenerations for this session. To explore unlimited, highly personalized ideas and expert gifting strategies, please upgrade to Dearly Premium."
            }
        session["regeneration_count"] += 1
        prompt_addition = "The user wants 3 DIFFERENT gift ideas. Do not repeat the previous ideas. Ensure they are still highly personalized concepts, not products."
        session["history"].append({"role": "user", "content": prompt_addition})
    else:
        session["history"].append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if session["context"]:
         ctx_note = f"Context gathered: {json.dumps(session['context'])}. Do not re-ask these."
         messages.append({"role": "system", "content": ctx_note})

    messages.extend(session["history"])

    global client
    if client is None:
        client = _get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.8, # Slightly higher for more creative ideas
            max_tokens=900,
        )
        raw = response.choices[0].message.content.strip()

        # Clean JSON
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].strip()

        # Check for trailing commas or other common LLM JSON errors and load
        try:
             result = json.loads(raw)
             if not isinstance(result, dict):
                 result = {"type": "conversation", "message": str(result)}
        except json.JSONDecodeError:
             # LLMs sometimes fail strict JSON. Attempt a simple fix or fallback
             result = {"type": "conversation", "message": raw if raw else "I was thinking so hard about the perfect gift that my brain got a little tangled! Could you tell me a little more about them?"}

        # Don't save paywall prompts to history to keep it clean if they restart
        if not is_regeneration:
            # We save the *user* message in the normal flow above. Here we save the *bot* reply.
            # We don't save the raw JSON string if it failed parsing, but let's assume valid JSON is saved.
            session["history"].append({"role": "assistant", "content": json.dumps(result)})
        else:
             session["history"].append({"role": "assistant", "content": json.dumps(result)})

        if result.get("type") == "gift_ideas" and result.get("ideas"):
            session["ideas"] = result["ideas"]
            if result.get("occasion"):
                 session["context"]["occasion"] = result["occasion"]

        if not is_regeneration:
             _extract_context(session, user_message)

        return result

    except ValueError as e:
        return {"type": "error", "message": f"⚠️ Configuration Error: {str(e)}. Please check your Streamlit Secrets."}
    except Exception as e:
        print(f"Error in chat_handler: {e}")
        return {"type": "error", "message": f"Dearly Logic Error: {str(e)}"}

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
