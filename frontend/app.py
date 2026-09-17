import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Drive File Assistant · TailorTalk",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stChatMessage {
        border-radius: 14px;
        padding: 4px 0;
    }
    .stChatInput > div {
        border-radius: 24px;
    }
    [data-testid="stSidebar"] {
        background-color: #f7f8fc;
    }
    .block-container {
        padding-top: 1.5rem;
    }
    .stCaption {
        color: #888;
        font-size: 0.78rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "backend_url" not in st.session_state:
    st.session_state.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

from components.chat import render_chat
from components.sidebar import render_sidebar

render_sidebar()
render_chat()