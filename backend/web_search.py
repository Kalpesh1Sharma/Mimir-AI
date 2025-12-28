import os
import requests
from typing import Dict, Any, List


class WebSearchQA:
    """
    Web-based factual QA using Tavily (primary) with safe fallbacks.
    """

    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")

        if not self.tavily_key:
            raise ImportError(
                "TAVILY_API_KEY not found in environment variables"
            )

    # ======================
    # PUBLIC ENTRY POINT
    # ======================
    def answer(self, query: str) -> Dict[str, Any]:
        results = self._search_tavily(query)

        if not results:
            return {
                "answer": "I couldn’t find reliable grounded information for this question.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {"tool": "web_search"},
            }

        # Simple synthesis (no hallucination)
        top = results[0]

        return {
            "answer": f"**{top['answer']}**",
            "sources": [top["source"]],
            "confidence": 0.85,
            "metadata": {"tool": "web_search"},
        }

    # ======================
    # TAVILY SEARCH
    # ======================
    def _search_tavily(self, query: str) -> List[Dict[str, str]]:
        url = "https://api.tavily.com/search"

        payload = {
            "api_key": self.tavily_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "include_sources": True,
            "max_results": 3,
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("results"):
                return []

            results = []

            for r in data["results"]:
                if r.get("answer"):
                    results.append({
                        "answer": r["answer"],
                        "source": r.get("url", "web"),
                    })

            return results

        except Exception:
            return []
