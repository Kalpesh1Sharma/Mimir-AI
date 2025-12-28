# backend/router.py

from typing import Dict, Any
import re


def route_query(
    text: str,
    persona: Dict[str, Any],
    mode: Dict[str, Any],
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    metadata = metadata or {}
    text_lower = text.lower().strip()

    routing = {
        "intent": "rag",              # 👈 NEW
        "use_retrieval": False,
        "domain": "general",
        "use_web_search": False,
        "use_file_qa": False,
        "use_creative": False,
        "notes": [],
    }

    # -------------------------------------------------
    # 1️⃣ PURE REASONING (math / logic)
    # -------------------------------------------------
    if re.search(r"\b\d+\s*[\+\-\*/]\s*\d+\b", text_lower):
        routing["intent"] = "reasoning"
        routing["notes"].append("Deterministic reasoning detected.")
        return routing

    # -------------------------------------------------
    # 2️⃣ STATIC KNOWLEDGE (no retrieval needed)
    # -------------------------------------------------
    static_patterns = [
        "opposite of",
        "capital of",
        "who won",
        "president of",
        "prime minister of",
        "fifa world cup",
        "ipl",
    ]

    if any(p in text_lower for p in static_patterns):
        routing["intent"] = "static_knowledge"
        routing["notes"].append("Static factual knowledge detected.")
        return routing

    # -------------------------------------------------
    # 3️⃣ Mode enforcement
    # -------------------------------------------------
    if mode.get("hard_rules", {}).get("requires_retrieval"):
        routing["use_retrieval"] = True
        routing["intent"] = "rag"
        routing["notes"].append("Factual mode requires retrieval.")

    # -------------------------------------------------
    # 4️⃣ Live / time-sensitive detection (REAL live)
    # -------------------------------------------------
    live_keywords = [
        "latest", "today", "current price",
        "live score", "breaking news",
        "right now"
    ]

    if any(k in text_lower for k in live_keywords):
        routing["intent"] = "web_search"
        routing["use_web_search"] = True
        routing["notes"].append("Live information detected.")

    # -------------------------------------------------
    # 5️⃣ File-based Q&A
    # -------------------------------------------------
    if metadata.get("has_attachments"):
        routing["intent"] = "file_qa"
        routing["use_file_qa"] = True
        routing["use_retrieval"] = True
        routing["notes"].append("User attachments detected.")

    # -------------------------------------------------
    # 6️⃣ Technical domain detection
    # -------------------------------------------------
    technical_keywords = [
        "python", "code", "faiss",
        "vector", "embedding", "rag",
        "database", "index",
    ]

    if any(k in text_lower for k in technical_keywords):
        routing["domain"] = "technical"
        routing["notes"].append("Technical keywords detected.")

    return routing
