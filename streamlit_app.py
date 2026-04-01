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
    page_title="Dearly — The Art of Meaningful Gifting",
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

# --- Custom Styling ($1000 Premium Look) ---
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
    /* Full Page Background */
    .stApp {{
        background-image: url("data:image/png;base64,{bg_image_base64}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        font-family: 'Outfit', sans-serif;
    }}

    /* Semi-transparent Overlay for Readability */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(255, 255, 255, 0.4); /* Subtle white veil */
        z-index: -1;
    }}

    /* Global Typography */
    h1, h2, h3, p, span, li, button {{
        font-family: 'Outfit', sans-serif !important;
        color: #2D3436 !important; /* High contrast dark grey */
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(220, 220, 220, 0.5);
    }}

    /* Chat Messages */
    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(200, 200, 200, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
        padding: 1.2rem;
    }}
    
    [data-testid="stChatMessageUser"] {{
        background-color: rgba(240, 248, 255, 0.9) !important; /* Light blue tint for user */
    }}

    /* Confidence Badge */
    .confidence-badge {{
        background: #EAF2F8;
        color: #2980B9;
        padding: 4px 12px;
        border-radius: 24px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
        border: 1px solid rgba(41, 128, 185, 0.2);
    }}

    /* Idea Card Styling */
    .idea-card {{
        background: white;
        border: 1px solid #EDEDED;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    .idea-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08);
        border-color: #B26B7D;
    }}
    
    .idea-title {{
        color: #B26B7D;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    
    .idea-reasoning {{
        color: #4A4A4A;
        font-size: 1rem;
        line-height: 1.6;
    }}

    /* Button Styling */
    .stButton>button {{
        border-radius: 12px;
        border: 1px solid #B26B7D;
        color: #B26B7D;
        transition: all 0.2s;
    }}
    .stButton>button:hover {{
        background-color: #FDF4F6;
        border-color: #B26B7D;
        color: #B26B7D;
    }}

    /* Hide Streamlit components */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if "session_id" not in st.session_state:
    st.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "regeneration_count" not in st.session_state:
    st.session_state.regeneration_count = 0

# --- Sidebar: History & Branding ---
with st.sidebar:
    st.image("https://files.python-hosted.org/packages/49/7c/8d3e2c3c6f4a8e0e7a1f8e8b/streamlit-1.56.0.tar.gz", width=0) # dummy for space
    st.title("🌸 Dearly")
    st.markdown("*Meaningful Gifting Assistant*")
    st.markdown("---")
    
    st.subheader("Successful Sessions")
    metrics = db.get_admin_metrics()
    recent_copies = metrics.get("recent_copies", [])
    
    if not recent_copies:
        st.info("No sessions yet. Generate and copy a note to see them here.")
    else:
        for copy in recent_copies:
            with st.expander(f"✨ {copy.get('idea_title', 'Gift')}"):
                st.caption(f"Reasoning: {copy.get('reasoning', 'N/A')}")

    st.markdown("---")
    if st.button("New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# --- Main Interface ---
st.title("Gifting Assistant")
st.markdown("### Hand-crafted gift concepts for the people you love.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.write(message["content"])
        elif message["type"] == "gift_ideas":
            st.write(message["message"])
            for idx, idea in enumerate(message["ideas"]):
                st.markdown(f"""
                <div class="idea-card">
                    <div class="confidence-badge">{idea.get('confidence_score', 90)}% Match</div>
                    <div class="idea-title">{idea['title']}</div>
                    <div class="idea-reasoning">{idea['reasoning']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Generate Note: {idea['title']}", key=f"btn_{message['id']}_{idx}"):
                    note_res = chat_handler.generate_note_for_idea(
                        st.session_state.session_id, 
                        idea['title'], 
                        idea['reasoning']
                    )
                    st.success("Custom Note Generated!")
                    st.text_area("Your Personalized Note", value=note_res["note"], height=100)
                    
                    if st.button("Copy & Record Success", key=f"copy_{message['id']}_{idx}"):
                        db.save_note_copy(st.session_state.session_id, idea['title'])
                        st.toast("Success recorded! Sidebar updated.")
                        time.sleep(1)
                        st.rerun()

# Chat Input
if prompt := st.chat_input("Ask Dearly something... (e.g., 'Gift for my mom's birthday')"):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Refining ideas..."):
            response = chat_handler.chat(st.session_state.session_id, prompt)
            
            if response["type"] == "conversation":
                st.write(response["message"])
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": response["message"]})
            
            elif response["type"] == "gift_ideas":
                st.write(response["message"])
                msg_id = str(uuid.uuid4())[:8]
                st.session_state.messages.append({
                    "role": "assistant", 
                    "type": "gift_ideas", 
                    "message": response["message"], 
                    "ideas": response["ideas"],
                    "id": msg_id
                })
                # Display new ones
                for idx, idea in enumerate(response["ideas"]):
                    st.markdown(f"""
                    <div class="idea-card">
                        <div class="confidence-badge">{idea.get('confidence_score', 85)}% Match</div>
                        <div class="idea-title">{idea['title']}</div>
                        <div class="idea-reasoning">{idea['reasoning']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.rerun()
                
            elif response["type"] == "paywall":
                st.warning(response["message"])
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": response["message"]})
            
            elif response["type"] == "guardrail":
                st.info(response["message"])
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": response["message"]})
            
            elif response["type"] == "error":
                st.error(f"Dearly Error: {response['message']}")
            
            else:
                st.error("Something went wrong.")
