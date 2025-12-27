# streamlit_app.py

import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Mimir",
    layout="centered",
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <h1 style="text-align:center;">🧠 Mimir</h1>
    <p style="text-align:center; color:gray;">
        A grounded, persona-adaptive RAG assistant
    </p>
    <hr>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SIDEBAR — CONTROLS
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🎛 Controls")

    # Persona selector
    persona = st.selectbox(
        "Persona",
        options=[
            "default",
            "strict_corporate",
            "emotional_support",
            "only_python",
            "historian",
        ],
        index=0,
    )

    # Mode toggle
    mode = st.radio(
        "Response mode",
        options=["factual", "creative"],
        index=0,
    )

    st.markdown("---")

    # File upload
    uploaded_files = st.file_uploader(
        "Upload files (session-based)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )

    if st.button("➕ Upload files"):
        if not uploaded_files:
            st.warning("Please select files first.")
        else:
            files = [
                ("files", (f.name, f.getvalue(), f.type))
                for f in uploaded_files
            ]

            resp = requests.post(
                f"{API_BASE}/files/upload",
                files=files,
            )

            if resp.status_code == 200:
                st.success("Files uploaded successfully.")
            else:
                st.error("Upload failed.")

    if st.button("🗑 Clear uploaded files"):
        requests.post(f"{API_BASE}/files/clear")
        st.success("Session cleared.")

    st.markdown("---")
    st.caption(
        "Mimir is a safety-first assistant.\n\n"
        "• Persona-adaptive\n"
        "• Factual & creative modes\n"
        "• File Q&A\n"
        "• Guarded web answers"
    )

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "chat" not in st.session_state:
    st.session_state.chat = []

# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_input = st.chat_input("Ask Mimir…")

if user_input:
    # User message
    st.session_state.chat.append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            resp = requests.post(
                f"{API_BASE}/query",
                json={
                    "query": user_input,
                    "persona": persona,
                    "mode": mode,
                },
            )

        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            confidence = data.get("confidence", 0.0)
            metadata = data.get("metadata", {})
        else:
            answer = "Something went wrong."
            sources = []
            confidence = 0.0
            metadata = {}

        st.markdown(answer, unsafe_allow_html=True)
        st.caption(f"Confidence: {confidence:.2f}")

        if sources:
            with st.expander("Sources"):
                for s in sources:
                    st.markdown(f"- {s}")

        if metadata.get("note") == "intentional_refusal":
            st.info("This response was intentionally limited to avoid misinformation.")

    # Save assistant message
    st.session_state.chat.append({
        "role": "assistant",
        "content": answer,
    })
