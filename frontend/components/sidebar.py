import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.markdown("## 📁 Drive File Assistant")
        st.markdown("*Powered by LangGraph + Groq + Google Drive*")
        st.divider()

        st.markdown("### 🔎 Search Tips")
        st.info(
            "**By name:** find invoice Q1\n\n"
            "**By type:** show all PDFs\n\n"
            "**By content:** files about payroll\n\n"
            "**By date:** files from last week\n\n"
            "**Combined:** PDF reports from this month"
        )

        st.divider()
        st.markdown("### 💬 Session")
        msg_count = len(st.session_state.get("messages", []))
        st.metric("Messages in chat", msg_count)

        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.markdown("### ⚙️ Backend URL")
        backend_url = st.text_input(
            "FastAPI URL",
            value=st.session_state.get("backend_url", "http://localhost:8000"),
            label_visibility="collapsed",
        )
        st.session_state["backend_url"] = backend_url

        st.divider()
        st.caption("TailorTalk Assignment · Built with LangGraph")