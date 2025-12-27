# backend/llm.py

from typing import List, Dict, Optional


class LLMClient:
    """
    LLM abstraction used ONLY for synthesis.

    This client must NEVER be used for:
    - retrieval
    - answering without context
    """

    def __init__(self, provider: str = "mock"):
        self.provider = provider

    def synthesize(
        self,
        query: str,
        chunks: List[Dict[str, str]],
        mode: str = "factual",
    ) -> str:
        """
        Synthesize an answer strictly from retrieved chunks.
        """

        # ---------- MOCK / FALLBACK ----------
        if self.provider == "mock":
            return self._mock_summarize(chunks)

        # ---------- REAL LLM (placeholder) ----------
        # You can plug OpenAI / Gemini / local LLM here later
        raise NotImplementedError("LLM provider not configured.")

    # ------------------------------------------------

    def _mock_summarize(self, chunks: List[Dict[str, str]]) -> str:
        """
        Deterministic fallback summarizer.
        """
        lines = []
        for c in chunks:
            text = c["text"].strip()
            if text:
                lines.append(text)

        return "\n\n".join(lines)
