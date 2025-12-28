

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st

from backend.assistant import MimirAssistant

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Mimir",
    layout="centered",
)

# --------------------------------------------------
# LOAD SECRETS (Streamlit Cloud compatible)
# --------------------------------------------------

if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

if "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# --------------------------------------------------
# INIT ASSISTANT (SESSION SAFE)
# --------------------------------------------------

if "mimir" not in st.session_state:
    st.session_state.mimir = MimirAssistant()

if "chat" not in st.session_state:
    st.session_state.chat = []

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
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🎛 Controls")

    persona = st.selectbox(
        "Persona",
        [
            "default",
            "emotional_support",
            "only_python",
        ],
    )

    mode = st.radio(
        "Mode",
        ["factual", "creative"],
        horizontal=True,
    )

    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )

    if st.button("➕ Upload files"):
        if uploaded_files:
            paths = []
            for f in uploaded_files:
                path = f"uploaded_{f.name}"
                with open(path, "wb") as out:
                    out.write(f.read())
                paths.append(path)

            st.session_state.mimir.ingest_files(paths)
            st.success("Files uploaded successfully")

    if st.button("🗑 Clear session"):
        st.session_state.mimir.clear_files()
        st.session_state.chat = []
        st.success("Session cleared")

    st.caption(
        "• Persona-aware reasoning\n"
        "• FAISS RAG\n"
        "• File Q&A\n"
        "• Safe web answers"
    )

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
    # user message
    st.session_state.chat.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            result = st.session_state.mimir.query(
                text=user_input,
                persona=persona,
                mode=mode,
            )

        answer = result.get("answer", "")
        sources = result.get("sources", [])
        confidence = result.get("confidence", 0.0)
        metadata = result.get("metadata", {})

        st.markdown(answer, unsafe_allow_html=True)
        st.caption(f"Confidence: {confidence:.2f}")

        if sources:
            with st.expander("Sources"):
                for s in sources:
                    st.markdown(f"- {s}")

        if metadata.get("note") == "intentional_refusal":
            st.info("This response was intentionally limited to avoid misinformation.")

    st.session_state.chat.append(
        {"role": "assistant", "content": answer}
    )
