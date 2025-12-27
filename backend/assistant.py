# backend/assistant.py

from dotenv import load_dotenv
load_dotenv()

import re
from typing import Dict, Optional, Any, List

from backend.router import route_query
from backend.personas import PersonaManager
from backend.modes import ModeManager
from backend.llm import LLMClient
from backend.tools.web_search import WebSearchTool
from backend.file_qa.file_qa import FileQASystem

from rag.embeddings import EmbeddingModel
from rag.retrieve import FaissRetriever


# -------------------------------
# Intent keywords
# -------------------------------

HISTORICAL_EVENTS = [
    "ipl",
    "world cup",
    "olympics",
    "election",
    "fifa",
    "final",
]

FACTUAL_PATTERNS = [
    "who is",
    "who was",
    "who won",
    "first",
    "founder",
    "president",
    "prime minister",
    "capital of",
    "when did",
    "where is",
    "name of",
]

EMOTION_WORDS = [
    "lonely", "sad", "anxious", "depressed", "down",
    "overwhelmed", "tired", "stressed", "hopeless",
    "empty", "hurt", "lost", "scared", "afraid"
]


class MimirAssistant:
    """
    FINAL Mimir Assistant (Intent-Reasoning Enabled)

    New capability:
    - Auto emotional intent detection for default persona

    Routing priority:
    0. Emotional intent (auto)
    1. Persona override (explicit)
    2. File Upload Q&A
    3. Explicit factual intent → Web + synthesis
    4. Guarded web queries
    5. Core RAG (technical knowledge)
    """

    def __init__(self):
        self.persona_manager = PersonaManager()
        self.mode_manager = ModeManager()

        self.llm = LLMClient(provider="mock")

        # Core RAG
        self.embedder = EmbeddingModel()
        self.retriever = FaissRetriever()

        # Web search (historical only)
        self.web_search = WebSearchTool()

        # File Q&A (session-based)
        self.file_qa = FileQASystem()

    # --------------------------------------------------
    # FILE SESSION API
    # --------------------------------------------------

    def ingest_files(self, file_paths: List[str]):
        self.file_qa.ingest_files(file_paths)

    def clear_files(self):
        self.file_qa.clear()

    # --------------------------------------------------
    # MAIN QUERY ENTRY
    # --------------------------------------------------

    def query(
        self,
        text: str,
        persona: str = "default",
        mode: str = "factual",
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        q_lower = text.lower()

        # --------------------------------------------------
        # 0️⃣ AUTO EMOTIONAL INTENT (DEFAULT PERSONA ONLY)
        # --------------------------------------------------

        if persona == "default":
            if any(word in q_lower for word in EMOTION_WORDS):
                return self._emotional_response(text, auto=True)

        # --------------------------------------------------
        # 1️⃣ PERSONA OVERRIDES (EXPLICIT)
        # --------------------------------------------------

        if persona == "emotional_support":
            return self._emotional_response(text, auto=False)

        if persona == "only_python":
            answer = self.llm.synthesize(
                query=f"Respond with Python code only.\n{text}",
                chunks=[],
                mode="code_only",
            )
            return {
                "answer": answer,
                "sources": [],
                "confidence": 0.85,
                "metadata": {
                    "persona": "only_python",
                    "routing": "llm_only",
                },
            }

        # --------------------------------------------------
        # 2️⃣ FILE Q&A
        # --------------------------------------------------

        if self.file_qa._files_loaded:
            return self.file_qa.answer(text)

        # --------------------------------------------------
        # 3️⃣ FACTUAL INTENT → WEB
        # --------------------------------------------------

        is_basic_factual = any(p in q_lower for p in FACTUAL_PATTERNS)
        if is_basic_factual:
            return self._handle_web_query(text, q_lower)

        # --------------------------------------------------
        # ROUTER (FALLBACK)
        # --------------------------------------------------

        routing = route_query(
            text=text,
            persona=self.persona_manager.load(persona),
            mode=self.mode_manager.load(mode),
            metadata=metadata or {},
        )

        # --------------------------------------------------
        # 4️⃣ WEB (HISTORICAL)
        # --------------------------------------------------

        if routing.get("use_web_search"):
            return self._handle_web_query(text, q_lower)

        # --------------------------------------------------
        # 5️⃣ CORE RAG (TECHNICAL)
        # --------------------------------------------------

        return self._handle_rag_query(text)

    # --------------------------------------------------
    # EMOTIONAL RESPONSE (SAFE + GUARANTEED)
    # --------------------------------------------------

    def _emotional_response(self, text: str, auto: bool) -> Dict[str, Any]:
        answer = self.llm.synthesize(
            query=text,
            chunks=[],
            mode="empathetic",
        )

        if not answer or not answer.strip():
            answer = (
                "I hear you. Whatever you're feeling right now is valid, "
                "and you don’t have to go through it alone. "
                "I’m here with you."
            )

        return {
            "answer": answer,
            "sources": [],
            "confidence": 0.8,
            "metadata": {
                "persona": "emotional_support" if not auto else "auto_emotional",
                "routing": "llm_only",
            },
        }

    # --------------------------------------------------
    # WEB HANDLING (WITH SYNTHESIS + BOLD ANSWER)
    # --------------------------------------------------

    def _handle_web_query(self, query: str, q_lower: str) -> Dict[str, Any]:
        is_live = any(x in q_lower for x in ["today", "yesterday", "latest", "recent"])

        if is_live and "ipl" in q_lower:
            return self._refusal(
                "I can’t reliably provide live or recent IPL updates right now. "
                "Please ask about a historical season or general rules."
            )

        if is_live:
            return self._refusal(
                "I can’t reliably access live information right now."
            )

        results = self.web_search.search_historical(query)
        if not results:
            return self._refusal(
                "I couldn’t find reliable factual information for this query."
            )

        context_chunks = [
            {"text": r["snippet"], "source": r["source"]}
            for r in results[:2]
        ]

        raw_answer = self.llm.synthesize(
            query=query,
            chunks=context_chunks,
            mode="factual",
        )

        answer = self._bold_first_sentence(raw_answer)

        return {
            "answer": answer,
            "sources": list({r["source"] for r in results[:2]}),
            "confidence": 0.9,
            "metadata": {
                "tool": "web_search",
                "mode": "factual_answer",
            },
        }

    # --------------------------------------------------
    # CORE RAG
    # --------------------------------------------------

    def _handle_rag_query(self, text: str) -> Dict[str, Any]:
        query_vec = self.embedder.embed(text)
        chunks = self.retriever.retrieve(
            query_vector=query_vec,
            domain="technical",
            top_k=8,
        )

        if not chunks:
            return {
                "answer": "I couldn’t find relevant technical context for this query.",
                "sources": [],
                "confidence": 0.3,
            }

        answer = self.llm.synthesize(
            query=text,
            chunks=chunks,
            mode="factual",
        )

        sources = list({c["source"] for c in chunks})

        return {
            "answer": answer,
            "sources": sources,
            "confidence": 0.9,
            "metadata": {
                "tool": "rag",
            },
        }

    # --------------------------------------------------
    # UTILITIES
    # --------------------------------------------------

    def _bold_first_sentence(self, text: str) -> str:
        if not text:
            return text

        sentences = re.split(r'(?<=[.!?])\s+', text, maxsplit=1)

        if len(sentences) == 1:
            return f"**{sentences[0]}**"

        return f"**{sentences[0]}** {sentences[1]}"

    def _refusal(self, message: str) -> Dict[str, Any]:
        return {
            "answer": message,
            "sources": [],
            "confidence": 0.4,
            "metadata": {
                "note": "intentional_refusal",
            },
        }
