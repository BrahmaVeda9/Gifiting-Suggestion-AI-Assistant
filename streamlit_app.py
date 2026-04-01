import streamlit as st
import sys
import os
import uuid
import json
import time
import base64
from dotenv import load_dotenv

# Load env before importing anything from phase_5_api
load_dotenv()

# Ensure we can import from phase_5_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "phase_5_api")))
import chat_handler
import database as db

# --- Page Configuration ---
st.set_page_config(
    page_title="Dearly | Premium Gifting",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Background Image Encoding ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Use the background image copied to root
bg_image_base64 = ""
if os.path.exists("./bg.png"):
    bg_image_base64 = get_base64_of_bin_file("./bg.png")

# --- Custom Styling (Clean and Readable Look) ---
overlay = "rgba(250, 246, 248, 0.75)" if bg_image_base64 else "rgba(250, 246, 248, 1.0)"
background_css = (
    f'background-image: linear-gradient({overlay}, {overlay}), url("data:image/png;base64,{bg_image_base64}");'
    if bg_image_base64
    else "background: linear-gradient(180deg, #fffafb 0%, #f8f5f7 100%);"
)

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    .stApp {{
        {background_css}
        background-size: cover;
        background-position: center;
        color: #2d1f25;
    }}

    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 1.25rem;
    }}

    h1, h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        color: #2e1f27 !important;
        letter-spacing: 0.01em;
    }}

    p, li, label, input, textarea, button {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* Keep Material Symbols icon font intact (sidebar arrows/chat avatars). */
    [class*="material-symbols"] {{
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", sans-serif !important;
    }}

    .hero-card {{
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(193, 148, 166, 0.25);
        border-radius: 18px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 10px 28px rgba(81, 45, 60, 0.08);
    }}

    .hero-title {{
        margin: 0 0 0.4rem 0;
        font-size: 2rem;
        line-height: 1.2;
    }}

    .hero-subtitle {{
        margin: 0;
        color: #5b4250;
        font-size: 1.02rem;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(251,246,249,0.97));
        border-right: 1px solid rgba(193, 148, 166, 0.2);
        padding-top: 0.7rem;
    }}

    .sidebar-brand-container {{
        text-align: left;
        padding: 0.4rem 0 0.7rem 0;
        margin-bottom: 0.3rem;
    }}

    .sidebar-brand-name {{
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        color: #8f4b67;
        margin: 0;
        line-height: 1.1;
    }}

    [data-testid="stChatMessage"] {{
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(196, 154, 170, 0.25);
        border-radius: 14px;
        margin-bottom: 0.9rem;
        padding: 0.95rem 1rem;
        box-shadow: 0 6px 20px rgba(50, 29, 39, 0.05);
    }}

    .confidence-badge {{
        background: #f7ecf1;
        color: #7d3f58;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.65rem;
        border: 1px solid rgba(168, 110, 133, 0.25);
    }}

    .idea-card {{
        background: #ffffff;
        border: 1px solid rgba(184, 142, 159, 0.25);
        border-radius: 14px;
        padding: 1.05rem 1.1rem;
        margin: 0.7rem 0 0.8rem 0;
        box-shadow: 0 8px 22px rgba(66, 36, 49, 0.06);
    }}

    .idea-title {{
        font-family: 'Playfair Display', serif;
        color: #2f2028;
        font-size: 1.27rem;
        margin-bottom: 0.55rem;
    }}

    .idea-reasoning {{
        color: #4f3d46;
        font-size: 0.99rem;
        line-height: 1.6;
    }}

    section[data-testid="stChatInput"] {{
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 12px;
        border: 1px solid rgba(176, 127, 146, 0.33);
        box-shadow: 0 8px 24px rgba(66, 36, 49, 0.08);
        padding: 0.2rem 0.4rem;
    }}

    .stButton > button {{
        border-radius: 10px;
        border: 1px solid #9c5c77;
        color: #8a4d68;
        background: #fff;
        font-weight: 600;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        border-color: #7c3f59;
        color: #fff;
        background: #8d4e69;
    }}

    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "regeneration_count" not in st.session_state:
    st.session_state["regeneration_count"] = 0

# --- Sidebar: History & Branding ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-container">
        <h1 class="sidebar-brand-name">Dearly</h1>
        <p style="font-size: 0.9rem; color: #888; font-style: italic;">The Art of Meaningful Gifting</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Previous Successes")
    metrics = db.get_admin_metrics()
    recent_copies = metrics.get("recent_copies", [])
    
    if not recent_copies:
        st.info("Your successful gifting journey begins here.")
    else:
        for copy in recent_copies:
            # Replaced icons with stable emojis
            with st.expander(f"✨ {copy.get('idea_title', 'Gift Inspiration')}"):
                st.caption(f"Reasoning: {copy.get('reasoning', 'N/A')}")

    st.markdown("---")
    if st.button("Start New Gifting Story", use_container_width=True):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = []
        st.rerun()

# --- Main Interface ---
st.markdown("""
<div class="hero-card">
    <h1 class="hero-title">Gifting Assistant</h1>
    <p class="hero-subtitle">Hand-crafted gift concepts for the people you love.</p>
</div>
""", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.write(message["content"])
        elif message["type"] == "gift_ideas":
            st.write(message["message"])
            for idx, idea in enumerate(message["ideas"]):
                st.markdown(f"""
                <div class="idea-card">
                    <div class="confidence-badge">✨ {idea.get('confidence_score', 90)}% Match Score</div>
                    <div class="idea-title">{idea['title']}</div>
                    <div class="idea-reasoning">{idea['reasoning']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Use a unique key with a descriptive prefix for stability
                col1, _ = st.columns([1, 2])
                with col1:
                    if st.button(f"Generate Boutique Note", key=f"note_gen_{message['id']}_{idx}"):
                        note_res = chat_handler.generate_note_for_idea(
                            st.session_state["session_id"], 
                            idea['title'], 
                            idea['reasoning']
                        )
                        st.session_state[f"note_cache_{message['id']}_{idx}"] = note_res["note"]
                
                # Check for cached note
                note_key = f"note_cache_{message['id']}_{idx}"
                if note_key in st.session_state:
                    st.markdown("---")
                    st.subheader("Your Personalized Gifting Note")
                    st.text_area("Final Polish", value=st.session_state[note_key], height=120)
                    
                    if st.button("Copy Note & Archive Success", key=f"save_success_{message['id']}_{idx}"):
                        db.save_note_copy(st.session_state["session_id"], idea['title'])
                        st.toast("Gift archive updated! Check your sidebar for the success.")
                        time.sleep(1.5)
                        st.rerun()

# Chat Input
if prompt := st.chat_input("Tell Dearly about your recipient..."):
    # Append user message
    st.session_state["messages"].append({"role": "user", "type": "text", "content": prompt})
    st.rerun()

# Process new user messages if any
if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
    last_prompt = st.session_state["messages"][-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner("Designing your gifting strategy..."):
            response = chat_handler.chat(st.session_state["session_id"], last_prompt)
            
            if response["type"] == "conversation":
                st.session_state["messages"].append({"role": "assistant", "type": "text", "content": response["message"]})
            
            elif response["type"] == "gift_ideas":
                msg_id = str(uuid.uuid4())[:8]
                st.session_state["messages"].append({
                    "role": "assistant", 
                    "type": "gift_ideas", 
                    "message": response["message"], 
                    "ideas": response["ideas"],
                    "id": msg_id
                })
                
            elif response["type"] == "paywall":
                st.session_state["messages"].append({"role": "assistant", "type": "text", "content": response["message"]})
            
            elif response["type"] == "guardrail":
                st.session_state["messages"].append({"role": "assistant", "type": "text", "content": response["message"]})
            
            elif response["type"] == "error":
                st.error(f"Designer Error: {response['message']}")
            
            st.rerun()
