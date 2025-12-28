import os
import requests
from dotenv import load_dotenv

load_dotenv()


class WebSearchQA:
    def __init__(self):
        self.serp_key = os.getenv("SERPAPI_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.google_key = os.getenv("GOOGLE_CSI_API_KEY")
        self.google_cx = os.getenv("GOOGLE_CSE_CX")

    # ======================
    # PUBLIC ENTRY
    # ======================
    def answer(self, query):
        # 1️⃣ SERP API
        if self.serp_key:
            result = self._serp_search(query)
            if result:
                return result

        # 2️⃣ Tavily
        if self.tavily_key:
            result = self._tavily_search(query)
            if result:
                return result

        # 3️⃣ Google CSE
        if self.google_key and self.google_cx:
            result = self._google_search(query)
            if result:
                return result

        return {
            "answer": "I couldn’t find reliable grounded information for this question.",
            "sources": [],
            "confidence": 0.3,
            "metadata": {"tool": "web_search"},
        }

    # ======================
    # SERP
    # ======================
    def _serp_search(self, query):
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "q": query,
                "api_key": self.serp_key,
                "engine": "google",
            }
            r = requests.get(url, params=params, timeout=8)
            data = r.json()

            answer_box = data.get("answer_box") or {}
            answer = answer_box.get("answer") or answer_box.get("snippet")

            if answer:
                return {
                    "answer": f"**{answer}**",
                    "sources": ["serpapi.com"],
                    "confidence": 0.85,
                    "metadata": {"tool": "serpapi"},
                }
        except Exception:
            pass

        return None

    # ======================
    # TAVILY
    # ======================
    def _tavily_search(self, query):
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_key,
                "query": query,
                "max_results": 3,
            }
            r = requests.post(url, json=payload, timeout=8)
            data = r.json()

            results = data.get("results", [])
            if results:
                return {
                    "answer": f"**{results[0]['content']}**",
                    "sources": [r["url"] for r in results],
                    "confidence": 0.75,
                    "metadata": {"tool": "tavily"},
                }
        except Exception:
            pass

        return None

    # ======================
    # GOOGLE CSE
    # ======================
    def _google_search(self, query):
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_key,
                "cx": self.google_cx,
                "q": query,
            }
            r = requests.get(url, params=params, timeout=8)
            data = r.json()

            items = data.get("items", [])
            if items:
                return {
                    "answer": f"**{items[0]['snippet']}**",
                    "sources": [i["link"] for i in items],
                    "confidence": 0.7,
                    "metadata": {"tool": "google_cse"},
                }
        except Exception:
            pass

        return None
