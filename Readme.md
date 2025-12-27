# 🧠 Mimir  
### A Grounded, Persona-Adaptive RAG Assistant

Mimir is a production-style AI assistant designed with **explicit reasoning, safety, and explainability** in mind.  
Unlike generic chatbots, Mimir uses **intent-aware routing**, **retrieval-augmented generation (RAG)**, and **persona control** to deliver reliable and predictable responses.

---

## 🚀 Features

### 🧩 Core Intelligence
- **Intent Reasoning Layer**
  - Detects factual, emotional, technical, and file-based queries
  - Routes queries explicitly instead of relying on model guessing

- **Retrieval-Augmented Generation (RAG)**
  - FAISS vector search over technical documents
  - Semantic retrieval using embeddings
  - Source attribution and confidence scoring

- **Auto Emotional Intent Detection**
  - Emotional queries are handled empathetically even in default mode
  - Predictable, explainable behavior (no hidden chain-of-thought)

---

### 🎭 Persona System
- `default` – neutral, safe responses
- `emotional_support` – empathetic support
- `only_python` – Python code only
- Extensible persona framework

---

### 🔄 Response Modes
- **Factual** – grounded, source-backed answers
- **Creative** – expressive, generative responses

---

### 📁 File Q&A (Session-Based)
- Upload PDF / TXT files
- Ask questions directly over uploaded content
- Automatic chunking + embedding + retrieval

---

### 🌐 Web Knowledge (Guarded)
- Historical factual queries supported
- Live / real-time queries intentionally refused
- Prevents hallucinations and stale answers

---

## 🧠 System Architecture

User Query\
↓\
Intent Reasoner\
↓\
Persona Logic\
↓\
Tool Selection \
• File Q&A \
• Web (historical only) \
• FAISS RAG \
• LLM fallback \
↓\
Grounded Response + Sources


---

## 🛠 Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Vector Store:** FAISS
- **Embeddings:** Sentence-level semantic embeddings
- **LLM:** Pluggable (mock / OpenAI-ready)
- **Search:** DuckDuckGo (historical only)

---

## ▶️ Running Locally

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/mimir.git
cd mimir
```
### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Start FastAPI backend
```bash
uvicorn api.main:app --reload
```
API: http://127.0.0.1:8000

Docs: http://127.0.0.1:8000/docs

### 4️⃣ Start Streamlit UI
```bash
streamlit run streamlit_app.py
```
## 🔒 Design Philosophy

❌ No uncontrolled hallucinations

❌ No implicit emotional assumptions

✅ Explicit reasoning

✅ Predictable behavior

✅ Interview-explainable architecture

## 📌 Why This Project Matters

This project demonstrates:

Real-world RAG architecture

Production-style safety controls

Intent-aware system design

Clear separation of concerns

Built to be explained, extended, and trusted.

## 👤 Author

Kalpesh Sharma\
Final-year B.Tech 