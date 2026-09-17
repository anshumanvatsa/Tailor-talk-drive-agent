import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import send_message

EXAMPLE_QUERIES = [
    "📁 What's in the Drive?",
    "📄 Show all PDFs",
    "📊 Recent spreadsheets",
    "🔍 Files about budget",
    "📅 Modified this week",
]

TOOL_LABELS = {
    "search_drive_files": "🔍 Drive Search",
    "get_file_details": "📋 File Details",
    "list_drive_summary": "📊 Drive Overview",
}


def render_chat():
    st.title("📁 Google Drive File Assistant")
    st.caption("Ask me to find files by name, type, content, or date — I'll search your Drive instantly.")

    st.markdown("**Quick searches:**")
    cols = st.columns(len(EXAMPLE_QUERIES))
    for i, query in enumerate(EXAMPLE_QUERIES):
        if cols[i].button(query, use_container_width=True, key=f"example_{i}"):
            st.session_state["pending_input"] = query

    st.divider()

    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tools_used"):
                labels = [TOOL_LABELS.get(t, t) for t in msg["tools_used"]]
                st.caption(f"Tools used: {' · '.join(labels)}")

    prompt = st.session_state.pop("pending_input", None) or st.chat_input(
        "Try: 'Find all invoices from last month' or 'Show me images'"
    )

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching Drive..."):
                import utils.api_client as api_client

                api_client.BACKEND_URL = st.session_state.get("backend_url", "http://localhost:8000")

                response, tools_used = send_message(
                    prompt,
                    st.session_state.messages[:-1],
                )

            st.markdown(response)
            if tools_used:
                labels = [TOOL_LABELS.get(t, t) for t in tools_used]
                st.caption(f"Tools used: {' · '.join(labels)}")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "tools_used": tools_used,
            }
        )