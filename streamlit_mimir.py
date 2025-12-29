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
# THEME
# ======================
st.markdown(
    """
    <style>
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

    h1, h2 {
        font-family: 'Georgia', serif;
        letter-spacing: 1px;
    }

    .rune-thinking {
        letter-spacing: 3px;
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

# ======================
# HELPERS
# ======================
def query_mimir(query, persona, mode):
    payload = {"query": query, "persona": persona, "mode": mode}
    r = requests.post(f"{API_URL}/query", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown("## 🧠 Mimir")
    st.caption("Keeper of wisdom")

    persona = st.selectbox(
        "Persona",
        ["default", "python_only", "emotional_support", "corporate", "historical_style"],
    )

    mode = st.radio("Mode", ["factual", "creative"], horizontal=True)

# ======================
# MAIN
# ======================
st.markdown(
    """
    <h2 style="text-align:center;">Mimir</h2>
    <p style="text-align:center;color:#9ca3af;">
    Keeper of knowledge · Speaker of truth
    </p>
    <div style="text-align:center;">ᚠᚢᚦᚨᚱᚲ</div>
    """,
    unsafe_allow_html=True,
)

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask, and I shall answer…")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        st.markdown("<span class='rune-thinking'>ᚦ ᚨ ᚱ ᚲ</span>", unsafe_allow_html=True)

        try:
            result = query_mimir(user_input, persona, mode)
            answer = result.get("answer", "")
            confidence = result.get("confidence", 0)

            st.markdown(answer)
            st.caption(f"Confidence: {confidence}")

            st.session_state.chat.append(
                {"role": "assistant", "content": answer}
            )
        except Exception:
            st.error("The runes are unclear.")
