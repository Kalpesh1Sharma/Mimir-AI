import streamlit as st
import requests

API_URL = "https://mimir-ai.onrender.com"

st.set_page_config(
    page_title="Mimir",
    page_icon="🧠",
    layout="centered",
)

# ======================
# WARM-UP PING
# ======================
def warm_up_backend():
    try:
        requests.get(f"{API_URL}/health", timeout=10)
        return True
    except Exception:
        return False

if "backend_warmed" not in st.session_state:
    st.session_state.backend_warmed = False

if not st.session_state.backend_warmed:
    with st.spinner("Waking up Mimir…"):
        st.session_state.backend_warmed = warm_up_backend()

# ======================
# HELPERS
# ======================
def query_mimir(query, persona, mode):
    payload = {
        "query": query,
        "persona": persona,
        "mode": mode,
    }
    r = requests.post(f"{API_URL}/query", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def upload_files(files):
    multipart = [("files", (f.name, f.getvalue(), f.type)) for f in files]
    r = requests.post(f"{API_URL}/files/upload", files=multipart, timeout=60)
    r.raise_for_status()
    return r.json()


def clear_files():
    requests.post(f"{API_URL}/files/clear", timeout=15)

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.title("🧠 Mimir")

    persona = st.selectbox(
        "Persona",
        ["default", "python_only", "emotional_support", "corporate", "historical_style"],
    )

    mode = st.radio("Mode", ["factual", "creative"], horizontal=True)

    st.divider()

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        type=["txt", "md"],
    )

    if uploaded_files and st.button("Index files"):
        with st.spinner("Indexing…"):
            res = upload_files(uploaded_files)
        st.success(f"{res['files_loaded']} file(s) indexed.")

    if st.button("Clear files"):
        clear_files()
        st.success("Files cleared.")

# ======================
# MAIN UI
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

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Mimir…")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                result = query_mimir(user_input, persona, mode)
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
            except Exception:
                st.error("Something went wrong.")
