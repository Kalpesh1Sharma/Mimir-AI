import os
import requests
from typing import Dict, Any, List


class WebSearchQA:
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.google_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.google_cx = os.getenv("GOOGLE_CSE_CX")

    # =========================
    # PUBLIC ENTRY
    # =========================
    def answer(self, query: str) -> Dict[str, Any]:
        # 1️⃣ Tavily
        if self.tavily_key:
            result = self._tavily_search(query)
            if result:
                return result

        # 2️⃣ SerpAPI
        if self.serpapi_key:
            result = self._serpapi_search(query)
            if result:
                return result

        # 3️⃣ Google CSE
        if self.google_key and self.google_cx:
            result = self._google_cse_search(query)
            if result:
                return result

        # 4️⃣ Refusal
        return {
            "answer": "I couldn’t find reliable grounded information for this question.",
            "sources": [],
            "confidence": 0.3,
            "metadata": {"tool": "web_fallback"},
        }

    # =========================
    # TAVILY
    # =========================
    def _tavily_search(self, query: str) -> Dict[str, Any] | None:
        try:
            r = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "max_results": 5,
                },
                timeout=10,
            )
            data = r.json()

            if data.get("answer"):
                return {
                    "answer": f"**{data['answer']}**",
                    "sources": [s["url"] for s in data.get("results", [])],
                    "confidence": 0.9,
                    "metadata": {"tool": "tavily"},
                }
        except Exception:
            pass

        return None

    # =========================
    # SERPAPI
    # =========================
    def _serpapi_search(self, query: str) -> Dict[str, Any] | None:
        try:
            r = requests.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google",
                    "q": query,
                    "api_key": self.serpapi_key,
                },
                timeout=10,
            )
            data = r.json()

            snippet = (
                data.get("answer_box", {}).get("answer")
                or data.get("answer_box", {}).get("snippet")
            )

            if snippet:
                return {
                    "answer": f"**{snippet}**",
                    "sources": [data.get("search_metadata", {}).get("google_url", "")],
                    "confidence": 0.85,
                    "metadata": {"tool": "serpapi"},
                }
        except Exception:
            pass

        return None

    # =========================
    # GOOGLE CSE
    # =========================
    def _google_cse_search(self, query: str) -> Dict[str, Any] | None:
        try:
            r = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={import os
import requests
from typing import Dict, Any, List


class WebSearchQA:
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.google_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.google_cx = os.getenv("GOOGLE_CSE_CX")

    # =========================
    # PUBLIC ENTRY
    # =========================
    def answer(self, query: str) -> Dict[str, Any]:
        # 1️⃣ Tavily
        if self.tavily_key:
            result = self._tavily_search(query)
            if result:
                return result

        # 2️⃣ SerpAPI
        if self.serpapi_key:
            result = self._serpapi_search(query)
            if result:
                return result

        # 3️⃣ Google CSE
        if self.google_key and self.google_cx:
            result = self._google_cse_search(query)
            if result:
                return result

        # 4️⃣ Refusal
        return {
            "answer": "I couldn’t find reliable grounded information for this question.",
            "sources": [],
            "confidence": 0.3,
            "metadata": {"tool": "web_fallback"},
        }

    # =========================
    # TAVILY
    # =========================
    def _tavily_search(self, query: str) -> Dict[str, Any] | None:
        try:
            r = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "max_results": 5,
                },
                timeout=10,
            )
            data = r.json()

            if data.get("answer"):
                return {
                    "answer": f"**{data['answer']}**",
                    "sources": [s["url"] for s in data.get("results", [])],
                    "confidence": 0.9,
                    "metadata": {"tool": "tavily"},
                }
        except Exception:
            pass

        return None

    # =========================
    # SERPAPI
    # =========================
    def _serpapi_search(self, query: str) -> Dict[str, Any] | None:
        try:
            r = requests.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google",
                    "q": query,
                    "api_key": self.serpapi_key,
                },
                timeout=10,
            )
            data = r.json()

            snippet = (
                data.get("answer_box", {}).get("answer")
                or data.get("answer_box", {}).get("snippet")
            )

            if snippet:
                return {
                    "answer": f"**{snippet}**",
                    "sources": [data.get("search_metadata", {}).get("google_url", "")],
                    "confidence": 0.85,
                    "metadata": {"tool": "serpapi"},
                }
        except Exception:
            pass

        return None

    # =========================
    # GOOGLE CSE
    # =========================
    def _google_cse_search(self, query: str) -> Dict[str, Any] | None:
        try:
            r = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    
                    "key": self.google_key,
                    "cx": self.google_cx,
                    "q": query,
                },
                timeout=10,
            )
            data = r.json()
            items = data.get("items", [])

            if items:
                return {
                    "answer": f"**{items[0]['snippet']}**",
                    "sources": [items[0]["link"]],
                    "confidence": 0.8,
                    "metadata": {"tool": "google_cse"},
                }
        except Exception:
            pass

        return None

                    "key": self.google_key,
                    "cx": self.google_cx,
                    "q": query,
                },
                timeout=10,
            )
            data = r.json()
            items = data.get("items", [])

            if items:
                return {
                    "answer": f"**{items[0]['snippet']}**",
                    "sources": [items[0]["link"]],
                    "confidence": 0.8,
                    "metadata": {"tool": "google_cse"},
                }
        except Exception:
            pass

        return None
