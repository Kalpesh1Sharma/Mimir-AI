# backend/web_search.py

import os
import requests
from typing import Dict, Any, List

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class WebSearchQA:
    """
    Live web factual QA using Tavily.
    Produces grounded answers with sources.
    """

    def __init__(self):
        if not TAVILY_API_KEY:
            raise RuntimeError("TAVILY_API_KEY not set")

    def answer(self, query: str) -> Dict[str, Any]:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "include_sources": True,
            },
            timeout=20,
        )

        data = response.json()

        if not data.get("answer"):
            return {
                "answer": "I couldn’t find reliable live information for this question.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {"tool": "web_search"},
            }

        return {
            "answer": f"**{data['answer']}**",
            "sources": [s["url"] for s in data.get("sources", [])],
            "confidence": 0.9,
            "metadata": {"tool": "web_search"},
        }
