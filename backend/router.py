# backend/router.py

from typing import Dict, Any


def route_query(
    text: str,
    persona: Dict[str, Any],
    mode: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    metadata = metadata or {}
    text_lower = text.lower()

    routing = {
        "use_web_search": False,
        "use_file_qa": False,
        "use_rag": False,
        "notes": [],
    }

    # Live / factual detection
    factual_keywords = [
        "who", "when", "where", "won",
        "president", "prime minister",
        "winner", "result", "capital",
        "population", "opposite",
    ]

    if any(k in text_lower for k in factual_keywords):
        routing["use_web_search"] = True
        routing["notes"].append("General factual query → web search")

    if metadata.get("has_attachments"):
        routing["use_file_qa"] = True
        routing["notes"].append("File QA activated")

    if mode == "creative":
        routing["notes"].append("Creative mode")

    return routing
