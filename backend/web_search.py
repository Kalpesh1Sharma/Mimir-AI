# backend/web_search.py

import os
import requests
from typing import Dict, Any


class WebSearchQA:
    """
    Web search fallback using Tavily API.
    """

    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.endpoint = "https://api.tavily.com/search"

        if not self.api_key:
            raise RuntimeError("TAVILY_API_KEY not set")

    def search(self, query: str) -> Dict[str, Any]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 5,
        }

        r = requests.post(self.endpoint, json=payload, timeout=15)
        r.raise_for_status()

        data = r.json()

        answer = data.get("answer")
        sources = [
            s.get("url") for s in data.get("results", []) if s.get("url")
        ]

        if not answer:
            return {}

        return {
            "answer": f"**{answer}**",
            "sources": sources,
            "confidence": 0.85,
            "metadata": {"tool": "web_search"},
        }
