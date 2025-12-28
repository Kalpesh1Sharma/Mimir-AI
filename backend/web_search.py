# backend/web_search.py

import os
import requests
from typing import Dict, Any, Optional


class WebSearchQA:
    """
    Web search QA with fallback:
    1) Tavily (primary)
    2) SerpAPI (secondary)
    """

    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")

        if not self.tavily_key and not self.serpapi_key:
            raise RuntimeError(
                "No web search API keys found (TAVILY_API_KEY / SERPAPI_KEY)"
            )

    # ======================
    # PUBLIC ENTRY
    # ======================
    def search(self, query: str) -> Dict[str, Any]:
        # 1️⃣ Try Tavily first
        if self.tavily_key:
            try:
                result = self._tavily_search(query)
                if result:
                    return result
            except Exception:
                pass  # fail silently → fallback

        # 2️⃣ Fallback to SerpAPI
        if self.serpapi_key:
            try:
                result = self._serpapi_search(query)
                if result:
                    return result
            except Exception:
                pass

        return {}

    # ======================
    # TAVILY
    # ======================
    def _tavily_search(self, query: str) -> Optional[Dict[str, Any]]:
        url = "https://api.tavily.com/search"

        payload = {
            "api_key": self.tavily_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 5,
        }

        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()

        data = r.json()
        answer = data.get("answer")

        if not answer:
            return None

        sources = [
            r.get("url")
            for r in data.get("results", [])
            if r.get("url")
        ]

        return {
            "answer": f"**{answer}**",
            "sources": sources,
            "confidence": 0.85,
            "metadata": {"tool": "tavily"},
        }

    # ======================
    # SERPAPI
    # ======================
    def _serpapi_search(self, query: str) -> Optional[Dict[str, Any]]:
        url = "https://serpapi.com/search"

        params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key,
            "num": 5,
        }

        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()

        data = r.json()

        # Prefer direct answer boxes
        answer = (
            data.get("answer_box", {}).get("answer")
            or data.get("answer_box", {}).get("snippet")
            or data.get("knowledge_graph", {}).get("description")
        )

        if not answer:
            organic = data.get("organic_results", [])
            if organic:
                answer = organic[0].get("snippet")

        if not answer:
            return None

        sources = [
            r.get("link")
            for r in data.get("organic_results", [])
            if r.get("link")
        ]

        return {
            "answer": f"**{answer}**",
            "sources": sources,
            "confidence": 0.8,
            "metadata": {"tool": "serpapi"},
        }
