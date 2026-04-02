import streamlit as st
import sys
import os
import uuid
import time
import base64
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "phase_5_api")))
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

bg_path = os.path.join(os.path.dirname(__file__), "bg.png")
bg_b64 = _b64(bg_path)

# ── CLEAN CSS (Minimal with no leakage) ──────────────────────────────────────
# Note: Using st.markdown + unsafe_allow_html at the top once.
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Outfit:wght@300;400;500&display=swap" rel="stylesheet">
<style>
    /* Global Styles */
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(rgba(252, 248, 250, 0.82), rgba(252, 248, 250, 0.82)), 
                    url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}

    /* Make all internal containers transparent to show the background */
    [data-testid="stHeader"], .stApp, [data-testid="stSidebar"], [data-testid="stVerticalBlock"] {{
        background: transparent !important;
        background-color: transparent !important;
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

    /* Zig-Zag text alignment and Capsule styling */
    .message-capsule {{
        padding: 12px 22px;
        border-radius: 28px;
        display: inline-block;
        max-width: 85%;
        font-size: 0.98rem;
        line-height: 1.5;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 12px rgba(81, 45, 60, 0.05);
    }}

    .user-capsule {{
        background: rgba(219, 188, 200, 0.7) !important; /* 70% transparent pink */
        border: 1px solid rgba(178, 107, 125, 0.2);
        color: #3d2b34;
        text-align: left;
    }}
    
    .assistant-capsule {{
        background: rgba(255, 255, 255, 0.7) !important; /* 70% transparent white */
        border: 1px solid rgba(178, 107, 125, 0.12);
        color: #3d2b34;
        text-align: left;
    }}

    .msg-row {{
        margin: 20px 0;
        display: flex;
        width: 100%;
    }}

    .user-row {{ justify-content: flex-end; }}
    .assistant-row {{ justify-content: flex-start; }}

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
st.markdown("<h1 style='text-align:center;'>Dearly</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-style:italic; color:#6a4c5a;'>Creating hand-crafted gift concepts for the people you love.</p>", unsafe_allow_html=True)
st.divider()

# ── CHAT ENGINE ────────────────────────────────────────────────────────────────
def render_message(role, type, content, msg_id=None, ideas=None, is_last=False):
    if role == "user":
        # Zig-Zag: User on Right with Capsule
        st.markdown(f"""
        <div class='msg-row user-row'>
            <div class='message-capsule user-capsule'>{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Zig-Zag: AI on Left with Capsule
        if type == "text":
            st.markdown(f"""
            <div class='msg-row assistant-row'>
                <div class='message-capsule assistant-capsule'>{content}</div>
            </div>""", unsafe_allow_html=True)
        elif type == "gift_ideas":
            st.markdown(f"""
            <div class='msg-row assistant-row'>
                <div class='message-capsule assistant-capsule'>{content}</div>
            </div>""", unsafe_allow_html=True)
            for idx, idea in enumerate(ideas):
                uid = f"{msg_id}_{idx}"
                strategy_name = idea.get('strategy_name', idea.get('title', 'Gifting Strategy'))
                example_gift = idea.get('example_gift', 'Thoughtful gift concept')
                
                st.markdown(f"""
                <div class="idea-card">
                    <div class="match-badge">✨ {idea.get('confidence_score', 88)}% CONFIDENCE SCORE</div>
                    <div class="idea-title">{strategy_name}</div>
                    <div class="idea-reasoning">{idea['reasoning']}</div>
                    <div style="margin-top:12px; padding:10px; background:rgba(178,107,125,0.05); border-radius:8px; border-left:3px solid #B26B7D;">
                        <span style="font-weight:600; color:#8f4b67; font-size:0.85rem; text-transform:uppercase;">Example Implementation:</span><br/>
                        <span style="font-size:0.95rem; color:#3d2b34;">{example_gift}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
                
                r_col, n_col = st.columns([1, 1])
                with r_col:
                    rating = st.feedback("stars", key=f"rate_{uid}")
                    if rating is not None:
                        db.save_rating(st.session_state["session_id"], strategy_name, int(rating) + 1)
                with n_col:
                    if st.button("Gifting Note 💌", key=f"note_{uid}", use_container_width=True):
                        res = chat_handler.generate_note_for_idea(
                            st.session_state["session_id"], strategy_name, f"{idea['reasoning']} Implementation: {example_gift}"
                        )
                        _note_dialog(strategy_name, res["note"])
            
            # REGENERATE (Only if it's the last message AND we actually have ideas to regenerate)
            if is_last and ideas:
                st.divider()
                if st.button("Regenerate Different Strategies ✨", key=f"regen_{msg_id}", use_container_width=True):
                    with st.spinner("Finding fresh frameworks..."):
                        # Pass history to ensure context is preserved on restart
                        res = chat_handler.dearly_chat(st.session_state["session_id"], "", is_regeneration=True, chat_history=st.session_state["messages"])
    
                    if res["type"] == "gift_ideas":
                        st.session_state["messages"].append({
                            "role": "assistant", "type": "gift_ideas",
                            "message": res["message"], "ideas": res["ideas"],
                            "id": str(uuid.uuid4())[:10],
                        })
                        st.rerun()
                    elif res["type"] == "paywall":
                        st.warning(res["message"])

# ── MAIN LOOP ──────────────────────────────────────────────────────────────────
for i, msg in enumerate(st.session_state["messages"]):
    render_message(
        msg["role"], 
        msg.get("type", "text"), 
        msg.get("content", msg.get("message", "")), 
        msg.get("id"), 
        msg.get("ideas"),
        is_last=(i == len(st.session_state["messages"]) - 1)
    )

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("I'm thinking of a gift for..."):
    st.session_state["messages"].append({"role": "user", "type": "text", "content": prompt})
    st.rerun()

# ── BOT PROCESSING ─────────────────────────────────────────────────────────────
msgs = st.session_state["messages"]
if msgs and msgs[-1]["role"] == "user":
    with st.spinner("Dearly is curating options..."):
        # Pass history to ensure context is preserved on restart
        response = chat_handler.dearly_chat(st.session_state["session_id"], msgs[-1]["content"], chat_history=msgs[:-1])
    
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
