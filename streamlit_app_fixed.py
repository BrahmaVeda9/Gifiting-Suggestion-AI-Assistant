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

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dearly | Premium Gifting",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND IMAGE (injected separately so base64 doesn't corrupt the CSS block)
# ─────────────────────────────────────────────────────────────────────────────
def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

if os.path.exists("./bg.png"):
    bg_b64 = _b64("./bg.png")
    # Inject background as a separate, tiny style block
    st.markdown(
        f"<style>.stApp{{background-image:linear-gradient(rgba(252,248,250,.88),rgba(252,248,250,.88)),url('data:image/png;base64,{bg_b64}')!important;background-size:cover!important;background-attachment:fixed!important;background-position:center!important;}}</style>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS (no giant base64 strings here)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Outfit:wght@300;400;500&display=swap" rel="stylesheet">
<style>
/* ── Typography ── */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; color: #3d2b34; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #3d2b34 !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,.55) !important;
    backdrop-filter: blur(18px);
    border-right: 1px solid rgba(178,107,125,.12);
}
.brand-name { font-family:'Playfair Display',serif; font-size:2rem; color:#8f4b67; line-height:1; }
.brand-tagline { font-size:.85rem; color:#9e7385; font-style:italic; }

/* ── Remove Streamlit default chat bubble background ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 2px 0 !important;
}

/* ── Zig-Zag custom bubble classes ── */
.row-user { display:flex; justify-content:flex-end; margin-bottom:.6rem; }
.row-ai   { display:flex; justify-content:flex-start; margin-bottom:.6rem; }

.bubble {
    display: inline-block;
    max-width: 75%;
    padding: .65rem 1rem;
    border-radius: 18px;
    line-height: 1.55;
    font-size: .98rem;
    word-break: break-word;
}
.bubble-user {
    background: rgba(246,230,235,.9);
    border: 1px solid rgba(178,107,125,.2);
    border-bottom-right-radius: 4px;
}
.bubble-ai {
    background: rgba(255,255,255,.85);
    border: 1px solid rgba(178,107,125,.12);
    border-bottom-left-radius: 4px;
    backdrop-filter: blur(4px);
}

/* ── Idea Cards ── */
.idea-card {
    background: rgba(255,255,255,.75);
    border: 1px solid rgba(178,107,125,.14);
    border-radius: 16px;
    padding: 18px 22px;
    margin: 12px 0;
    box-shadow: 0 6px 24px rgba(81,45,60,.05);
    backdrop-filter: blur(4px);
    transition: transform .25s, border-color .25s;
}
.idea-card:hover { transform:translateY(-3px); border-color:#B26B7D; background:rgba(255,255,255,.9); }
.match-badge {
    background:#f7ecf1; color:#7d3f58; font-size:.72rem; font-weight:600;
    letter-spacing:.06em; padding:3px 10px; border-radius:999px;
    border:1px solid rgba(168,110,133,.22); display:inline-block; margin-bottom:8px;
}
.idea-title { font-family:'Playfair Display',serif; font-size:1.25rem; color:#3d2b34; margin-bottom:5px; }
.idea-reasoning { font-size:.95rem; color:#594048; line-height:1.62; }

/* ── Buttons ── */
.stButton>button {
    border-radius:11px; border:1px solid #B26B7D; color:#B26B7D;
    background:rgba(255,255,255,.82); font-weight:500; font-size:.9rem; transition:all .2s;
}
.stButton>button:hover { background:#B26B7D; color:#fff; box-shadow:0 4px 12px rgba(178,107,125,.25); }

/* ── Chat Input ── */
[data-testid="stChatInput"] textarea {
    background:rgba(255,255,255,.9) !important;
    border:1px solid rgba(178,107,125,.2) !important;
    border-radius:14px !important;
}

/* ── Misc ── */
#MainMenu, footer, .stDeployButton { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DIALOG — Personalised Note with Copy
# ─────────────────────────────────────────────────────────────────────────────
@st.dialog("Your Personalised Gifting Note ✉️")
def _note_dialog(title: str, note: str):
    st.markdown(f"**For:** {title}", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"*{note}*", unsafe_allow_html=True)
    st.divider()
    st.caption("Use the copy button on the code block below to copy your note instantly.")
    st.code(note, language=None)   # st.code has a built-in copy button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Archive as Success 🌸", use_container_width=True):
            db.save_note_copy(st.session_state["session_id"], title)
            st.toast("Archived! Check your sidebar.")
            time.sleep(1)
            st.rerun()
    with col2:
        if st.button("Close", use_container_width=True):
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p class="brand-name">Dearly</p>'
        '<p class="brand-tagline">The Art of Meaningful Gifting</p>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.subheader("Boutique Successes")
    metrics = db.get_admin_metrics()
    recent = metrics.get("recent_copies", [])
    if not recent:
        st.caption("Your gifting successes will appear here.")
    else:
        for item in recent:
            with st.expander(f"⭐ {item.get('idea_title','Gift')}"):
                avg = metrics["per_idea_avg_rating"].get(item.get("idea_title"), None)
                if avg:
                    st.caption(f"Avg rating: {avg:.1f} ⭐")
    st.divider()
    if st.button("Start New Conversation", use_container_width=True):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = []
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='margin-bottom:2px;'>Gifting Assistant</h1>"
    "<p style='color:#6a4c5a;font-size:1.05rem;font-style:italic;margin-top:0;'>"
    "Creating hand-crafted gift concepts for the people you love.</p>",
    unsafe_allow_html=True,
)
st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _text_bubble(role: str, text: str):
    css = "row-user" if role == "user" else "row-ai"
    bubble = "bubble-user" if role == "user" else "bubble-ai"
    st.markdown(
        f'<div class="{css}"><div class="bubble {bubble}">{text}</div></div>',
        unsafe_allow_html=True,
    )

def _render_ideas(msg: dict):
    _text_bubble("assistant", msg["message"])
    for idx, idea in enumerate(msg["ideas"]):
        uid = f"{msg['id']}_{idx}"
        st.markdown(f"""
        <div class="idea-card">
            <div class="match-badge">✨ {idea.get('confidence_score', 88)}% MATCH</div>
            <div class="idea-title">{idea['title']}</div>
            <div class="idea-reasoning">{idea['reasoning']}</div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns([1, 1])
        with c1:
            rating = st.feedback("stars", key=f"rate_{uid}")
            if rating is not None:
                db.save_rating(st.session_state["session_id"], idea["title"], int(rating) + 1)
                st.toast(f"{'⭐' * (int(rating)+1)} — saved to Supabase!")
        with c2:
            if st.button("Personalised Note 💌", key=f"note_{uid}", use_container_width=True):
                res = chat_handler.generate_note_for_idea(
                    st.session_state["session_id"], idea["title"], idea["reasoning"]
                )
                _note_dialog(idea["title"], res["note"])

    st.divider()
    if st.button("Explore Different Options ✨", key=f"regen_{msg['id']}", use_container_width=True):
        with st.spinner("Searching for fresh concepts..."):
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

# ─────────────────────────────────────────────────────────────────────────────
# RENDER ALL MESSAGES
# ─────────────────────────────────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    if msg["type"] == "text":
        _text_bubble(msg["role"], msg["content"])
    elif msg["type"] == "gift_ideas":
        _render_ideas(msg)

# ─────────────────────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Tell Dearly about your recipient..."):
    st.session_state["messages"].append({"role": "user", "type": "text", "content": prompt})
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# BOT PROCESSING
# ─────────────────────────────────────────────────────────────────────────────
msgs = st.session_state["messages"]
if msgs and msgs[-1]["role"] == "user":
    with st.spinner("Dearly is thinking..."):
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
                     "content": response.get("message", "Let me try that again!")})
    st.rerun()

