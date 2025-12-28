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
# SIDEBAR STATE
# ======================
if "theme" not in st.session_state:
    st.session_state.theme = "Mimir"

# ======================
# THEME TOGGLE
# ======================
with st.sidebar:
    st.markdown("## 🧠 Mimir")

    st.session_state.theme = st.radio(
        "Interface Style",
        ["Mimir", "Minimal"],
        horizontal=True,
    )

# ======================
# THEMES
# ======================
if st.session_state.theme == "Mimir":
    st.markdown(
        """
        <style>
        /* Background with subtle rune texture */
        .stApp {
            background:
              radial-gradient(circle at 20% 20%, rgba(255,255,255,0.02), transparent 40%),
              radial-gradient(circle at 80% 80%, rgba(255,255,255,0.015), transparent 40%),
              #0e1117;
            color: #e5e7eb;
        }

        section[data-testid="stSidebar"] {
            background-color: #111827;
            border-right: 1px solid #1f2937;
        }

        h1, h2, h3 {
            font-family: 'Georgia', serif;
            letter-spacing: 0.5px;
        }

        .stChatMessage {
            background-color: #111827;
            border-radius: 12px;
            padding: 10px;
            border: 1px solid #1f2937;
        }

        button[kind="primary"] {
            background-color: #7c2d12;
            border: none;
        }

        input, textarea {
            background-color: #020617 !important;
            color: #e5e7eb !important;
            border-radius: 8px;
            border: 1px solid #1f2937 !important;
        }

        /* Rune typing animation */
        .rune-thinking {
            font-family: 'Georgia', serif;
            letter-spacing: 2px;
            animation: glow 1.5s infinite alternate;
        }

        @keyframes glow {
            from { opacity: 0.4; }
            to { opacity: 1; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #ffffff;
            color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ======================
# HELPERS
# ======================
def query_mimir(query: str, persona: str, mode: str):
    payload = {"query": query, "persona": persona, "mode": mode}
    r = requests.post(f"{API_URL}/query", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def upload_files(files):
    multipart = [("files", (f.name, f.getvalue(), f.type)) for f in files]
    r = requests.post(f"{API_URL}/files/upload", files=multipart, timeout=60)
    r.raise_for_status()
    return r.json()


def clear_files():
    r = requests.post(f"{API_URL}/files/clear", timeout=15)
    r.raise_for_status()

# ======================
# SIDEBAR CONTROLS
# ======================
with st.sidebar:
    st.markdown("### ᚦ Control Runes")

    persona = st.selectbox(
        "Persona",
        ["default", "python_only", "emotional_support", "corporate", "historical_style"],
    )

    mode = st.radio("Mode", ["factual", "creative"], horizontal=True)

    st.markdown("ᚠᚢᚦᚨᚱᚲ")
    uploaded_files = st.file_uploader("📎 Knowledge scrolls", accept_multiple_files=True)

    if uploaded_files:
        if st.button("Bind knowledge"):
            with st.spinner("Engraving runes..."):
                upload_files(uploaded_files)
            st.success("Knowledge bound.")

    if st.button("Clear knowledge"):
        clear_files()
        st.warning("Knowledge cleared.")

# ======================
# HEADER
# ======================
st.markdown(
    """
    <h2 style="text-align:center;">Mimir</h2>
    <p style="text-align:center;color:#9ca3af;">
    Keeper of wisdom · Speaker of truth
    </p>
    <div style="text-align:center;">ᚠᚢᚦᚨᚱᚲ</div>
    """,
    unsafe_allow_html=True,
)

# ======================
# CHAT
# ======================
if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask, and I shall answer...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        st.markdown("<span class='rune-thinking'>ᚦ ᚨ ᚱ ᚲ</span>", unsafe_allow_html=True)

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
            st.session_state.chat.append({"role": "assistant", "content": answer})

        except Exception:
            st.error("The runes are unclear. Try again.")
