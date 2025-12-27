# backend/tools/web_search.py

import os
import requests
from typing import List, Dict


class WebSearchTool:
    """
    REPL-safe web search.

    Rules:
    - Tavily ONLY for live queries
    - Serp / Google ONLY for historical queries
    - NO DuckDuckGo (removed completely)
    """

    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.google_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.google_cx = os.getenv("GOOGLE_CSE_CX")

    # --------------------------------------------------

    def search_live(self, query: str) -> List[Dict[str, str]]:
        """Live queries → Tavily only"""
        if not self.tavily_key:
            return []

        try:
            r = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": self.max_results,
                },
                timeout=3,
            )
            r.raise_for_status()
            data = r.json()

            return [
                {
                    "title": x.get("title", ""),
                    "snippet": x.get("content", ""),
                    "source": x.get("url", ""),
                }
                for x in data.get("results", [])
            ]
        except Exception:
            return []

    # --------------------------------------------------

    def search_historical(self, query: str) -> List[Dict[str, str]]:
        """Historical queries → Serp → Google"""
        providers = [self._search_serpapi, self._search_google]

        for provider in providers:
            try:
                results = provider(query)
                if results:
                    return results
            except Exception:
                continue

        return []

    # --------------------------------------------------

    def _search_serpapi(self, query: str):
        if not self.serpapi_key:
            return []

        r = requests.get(
            "https://serpapi.com/search.json",
            params={
                "q": query,
                "engine": "google",
                "api_key": self.serpapi_key,
                "num": self.max_results,
            },
            timeout=3,
        )
        r.raise_for_status()
        data = r.json()

        return [
            {
                "title": x.get("title", ""),
                "snippet": x.get("snippet", ""),
                "source": x.get("link", ""),
            }
            for x in data.get("organic_results", [])
        ]

    # --------------------------------------------------

    def _search_google(self, query: str):
        if not (self.google_key and self.google_cx):
            return []

        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "q": query,
                "key": self.google_key,
                "cx": self.google_cx,
                "num": self.max_results,
            },
            timeout=3,
        )
        r.raise_for_status()
        data = r.json()

        return [
            {
                "title": x.get("title", ""),
                "snippet": x.get("snippet", ""),
                "source": x.get("link", ""),
            }
            for x in data.get("items", [])
        ]
