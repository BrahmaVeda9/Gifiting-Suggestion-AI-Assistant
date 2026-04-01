import streamlit as st
import sys
import os
import uuid
import time
import base64
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "phase_5_api")))
import chat_handler
import database as db

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dearly | Premium Gifting",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── BACKGROUND IMAGE (base64) ──────────────────────────────────────────────
def _b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

bg_b64 = _b64("./bg.png")

# ── CLEAN CSS (Minimal with no leakage) ──────────────────────────────────────
# Note: Using st.markdown + unsafe_allow_html at the top once.
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Outfit:wght@300;400;500&display=swap" rel="stylesheet">
<style>
    /* Global Styles */
    .stApp {{
        background-image: linear-gradient(rgba(252,248,250,0.87), rgba(252,248,250,0.87)), url("data:image/png;base64,{bg_b64}");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif !important;
        color: #3d2b34;
    }}
    
    h1, h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        color: #3d2b34 !important;
    }}

    /* Transparent containers */
    [data-testid="stVerticalBlock"] {{
        background: transparent !important;
    }}
    
    /* Idea Cards */
    .idea-card {{
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(178, 107, 125, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin-top: 10px;
        margin-bottom: 5px;
        box-shadow: 0 4px 15px rgba(81, 45, 60, 0.04);
        backdrop-filter: blur(10px);
    }}
    
    .match-badge {{
        background: #f7ecf1;
        color: #8f4b67;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 8px;
    }}
    
    .idea-title {{
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        margin-bottom: 8px;
    }}

    .idea-reasoning {{
        font-size: 0.95rem;
        color: #594048;
        line-height: 1.6;
    }}

    /* Zig-Zag text alignment (for messages when no bubbles) */
    .user-text {{
        text-align: right;
        font-weight: 500;
    }}
    
    .assistant-text {{
        text-align: left;
    }}

    /* Clean Sidebar */
    section[data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px);
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 12px;
        border: 1px solid #B26B7D !important;
        color: #B26B7D !important;
        background: white !important;
    }}
    .stButton > button:hover {{
        background: #B26B7D !important;
        color: white !important;
    }}

    /* Remove Streamlit default chat chrome */
    [data-testid="stChatMessage"] {{
        background: transparent !important;
    }}
    
    #MainMenu, footer, .stDeployButton {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── NOTE DIALOG ─────────────────────────────────────────────────────────────
@st.dialog("Your Personalised Gifting Note ✉️")
def _note_dialog(title, note):
    st.markdown(f"**For:** {title}")
    st.divider()
    st.markdown(f"*{note}*")
    st.divider()
    st.caption("Use the copy icon on the block below to copy your note.")
    st.code(note, language=None)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Archive as Success 🌸", use_container_width=True):
            db.save_note_copy(st.session_state["session_id"], title)
            st.toast("Success! Check your sidebar.")
            time.sleep(1)
            st.rerun()
    with col2:
        if st.button("Close", use_container_width=True):
            st.rerun()

# ── SESSION MANAGEMENT ───────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<h1 style='color:#8f4b67; margin-bottom:0;'>Dearly</h1>
    <p style='font-style:italic; font-size:0.9rem; margin-top:0;'>The Art of Giving</p>""", unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Boutique Successes")
    metrics = db.get_admin_metrics()
    recent = metrics.get("recent_copies", [])
    if not recent:
        st.caption("Successful gifts will appear here.")
    else:
        for item in recent:
            with st.expander(f"⭐ {item.get('idea_title', 'Gift')}"):
                avg = metrics["per_idea_avg_rating"].get(item.get("idea_title"), None)
                if avg:
                    st.caption(f"Rating: {avg:.1f} ⭐")
    
    st.divider()
    if st.button("Start New Conversation", use_container_width=True):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = []
        st.rerun()

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>Gifting Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-style:italic; color:#6a4c5a;'>Creating hand-crafted gift concepts for the people you love.</p>", unsafe_allow_html=True)
st.divider()

# ── CHAT ENGINE ────────────────────────────────────────────────────────────────
def render_message(role, type, content, msg_id=None, ideas=None):
    if role == "user":
        # Zig-Zag: User on Right
        c1, c2 = st.columns([1, 4])
        with c2:
            st.markdown(f"<div class='user-text'>{content}</div>", unsafe_allow_html=True)
    else:
        # Zig-Zag: AI on Left
        c1, c2 = st.columns([4, 1])
        with c1:
            if type == "text":
                st.markdown(f"<div class='assistant-text'>{content}</div>", unsafe_allow_html=True)
            elif type == "gift_ideas":
                st.markdown(f"<div class='assistant-text'>{content}</div>", unsafe_allow_html=True)
                for idx, idea in enumerate(ideas):
                    uid = f"{msg_id}_{idx}"
                    st.markdown(f"""
                    <div class="idea-card">
                        <div class="match-badge">✨ {idea.get('confidence_score', 88)}% MATCH</div>
                        <div class="idea-title">{idea['title']}</div>
                        <div class="idea-reasoning">{idea['reasoning']}</div>
                    </div>""", unsafe_allow_html=True)
                    
                    r_col, n_col = st.columns([1, 1])
                    with r_col:
                        rating = st.feedback("stars", key=f"rate_{uid}")
                        if rating is not None:
                            db.save_rating(st.session_state["session_id"], idea["title"], int(rating) + 1)
                            st.toast(f"{'⭐'*(int(rating)+1)} rated! Persisted in Supabase.")
                    with n_col:
                        if st.button("Gifting Note 💌", key=f"note_{uid}", use_container_width=True):
                            res = chat_handler.generate_note_for_idea(
                                st.session_state["session_id"], idea["title"], idea["reasoning"]
                            )
                            _note_dialog(idea["title"], res["note"])
                
                # REGENERATE
                st.divider()
                if st.button("Regenerate Different Ideas ✨", key=f"regen_{msg_id}", use_container_width=True):
                    with st.spinner("Finding fresh concepts..."):
                        res = chat_handler.chat(st.session_state["session_id"], "", is_regeneration=True)
                    if res["type"] == "gift_ideas":
                        st.session_state["messages"].append({
                            "role": "assistant", "type": "gift_ideas",
                            "message": res["message"], "ideas": res["ideas"],
                            "id": str(uuid.uuid4())[:8],
                        })
                        st.rerun()
                    elif res["type"] == "paywall":
                        st.warning(res["message"])

# ── MAIN LOOP ──────────────────────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    render_message(
        msg["role"], 
        msg.get("type", "text"), 
        msg.get("content", msg.get("message", "")), 
        msg.get("id"), 
        msg.get("ideas")
    )

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("I'm thinking of a gift for..."):
    st.session_state["messages"].append({"role": "user", "type": "text", "content": prompt})
    st.rerun()

# ── BOT PROCESSING ─────────────────────────────────────────────────────────────
msgs = st.session_state["messages"]
if msgs and msgs[-1]["role"] == "user":
    with st.spinner("Dearly is curateing options..."):
        response = chat_handler.chat(st.session_state["session_id"], msgs[-1]["content"])
    
    if response["type"] == "conversation":
        msgs.append({"role": "assistant", "type": "text", "content": response["message"]})
    elif response["type"] == "gift_ideas":
        msgs.append({
            "role": "assistant", "type": "gift_ideas",
            "message": response["message"], "ideas": response["ideas"],
            "id": str(uuid.uuid4())[:8],
        })
    else:
        msgs.append({"role": "assistant", "type": "text",
                     "content": response.get("message", "Ready to help!")})
    st.rerun()
