import streamlit as st
import requests

# ======================
# CONFIG
# ======================
API_URL = "https://mimir-ai.onrender.com"

st.set_page_config(
    page_title="Mimir",
    page_icon="🧠",
    layout="centered",
)

# ======================
# HELPERS
# ======================
def query_mimir(query: str, persona: str, mode: str):
    payload = {
        "query": query,
        "persona": persona,
        "mode": mode,
    }
    r = requests.post(f"{API_URL}/query", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def upload_files(files):
    multipart = []
    for f in files:
        multipart.append(
            ("files", (f.name, f.getvalue(), f.type))
        )
    r = requests.post(
        f"{API_URL}/files/upload",
        files=multipart,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def clear_files():
    r = requests.post(f"{API_URL}/files/clear", timeout=15)
    r.raise_for_status()
    return r.json()

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.title("🧠 Mimir")

    persona = st.selectbox(
        "Persona",
        options=[
            "default",
            "python_only",
            "emotional_support",
            "corporate",
            "historical_style",
        ],
        index=0,
    )

    mode = st.radio(
        "Mode",
        options=["factual", "creative"],
        horizontal=True,
    )

    st.divider()

    uploaded_files = st.file_uploader(
        "📎 Upload files",
        accept_multiple_files=True,
        type=["txt", "md"],
    )

    if uploaded_files:
        if st.button("Index uploaded files"):
            with st.spinner("Indexing files..."):
                res = upload_files(uploaded_files)
            st.success(f"{res['files_loaded']} file(s) indexed.")

    if st.button("Clear uploaded files"):
        clear_files()
        st.success("Uploaded files cleared.")

# ======================
# MAIN CHAT UI
# ======================
st.markdown(
    """
    <h2 style="text-align:center;">Mimir</h2>
    <p style="text-align:center;color:gray;">
    A persona-adaptive RAG assistant
    </p>
    """,
    unsafe_allow_html=True,
)

if "chat" not in st.session_state:
    st.session_state.chat = []

# Display chat history
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask Mimir…")

if user_input:
    # Show user message
    st.session_state.chat.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                result = query_mimir(
                    user_input,
                    persona=persona,
                    mode=mode,
                )

                answer = result.get("answer", "")
                sources = result.get("sources", [])
                confidence = result.get("confidence", 0)

                st.markdown(answer)

                if sources:
                    with st.expander("Sources"):
                        for s in sources:
                            st.markdown(f"- {s}")

                st.caption(f"Confidence: {confidence}")

                st.session_state.chat.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                error_msg = "Something went wrong. Please try again."
                st.error(error_msg)
                st.session_state.chat.append(
                    {"role": "assistant", "content": error_msg}
                )
