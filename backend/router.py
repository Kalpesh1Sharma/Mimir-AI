# backend/router.py

from typing import Dict, Any


def route_query(
    text: str,
    persona: Dict[str, Any],
    mode: Dict[str, Any],
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    metadata = metadata or {}
    text_lower = text.lower()

    routing = {
        "use_retrieval": False,
        "domain": "general",
        "use_web_search": False,
        "use_file_qa": False,
        "use_creative": False,
        "notes": [],
    }

    # ---- Mode enforcement ----
    if mode.get("hard_rules", {}).get("requires_retrieval"):
        routing["use_retrieval"] = True
        routing["notes"].append("Factual mode requires retrieval.")

    # ---- Live / time-sensitive detection ----
    live_keywords = [
        "latest", "today", "yesterday",
        "price", "cost", "score",
        "news", "current", "won"
    ]

    if any(k in text_lower for k in live_keywords):
        routing["use_web_search"] = True
        routing["use_retrieval"] = False
        routing["notes"].append("Live information detected → web search.")

    # ---- File-based Q&A ----
    if metadata.get("has_attachments"):
        routing["use_file_qa"] = True
        routing["use_retrieval"] = True
        routing["notes"].append("User attachments detected.")

    # ---- Technical detection ----
    technical_keywords = [
        "python", "code", "faiss",
        "vector", "embedding", "rag",
        "database", "index",
    ]

    if any(k in text_lower for k in technical_keywords):
        routing["domain"] = "technical"
        routing["notes"].append("Technical keywords detected.")

    return routing
