from typing import List, Dict, Any
from pathlib import Path

from backend.file_qa.index import FileFaissIndex


class FileQASystem:
    """
    Handles document ingestion and question answering over uploaded files.
    """

    def __init__(self):
        self.index = FileFaissIndex()
        self._files_loaded = False

    # ======================
    # FILE INGESTION
    # ======================
    def ingest_files(self, file_paths: List[str]):
        texts = []
        metadatas = []

        for path in file_paths:
            p = Path(path)
            if not p.exists():
                continue

            content = p.read_text(encoding="utf-8", errors="ignore")

            # Simple chunking (safe + fast)
            chunks = self._chunk_text(content)

            for c in chunks:
                texts.append(c)
                metadatas.append({"source": p.name})

        if texts:
            self.index.build(texts, metadatas)
            self._files_loaded = True

    # ======================
    # ANSWER
    # ======================
    def answer(self, query: str) -> Dict[str, Any]:
        results = self.index.search(query)

        if not results:
            return {
                "answer": "No relevant information found in uploaded files.",
                "sources": [],
                "confidence": 0.3,
            }

        context = "\n\n".join(r["text"] for r in results)

        return {
            "answer": context,
            "sources": list({r["metadata"]["source"] for r in results}),
            "confidence": 0.9,
        }

    # ======================
    # HELPERS
    # ======================
    def has_files(self) -> bool:
        return self._files_loaded

    def _chunk_text(self, text: str, size: int = 500) -> List[str]:
        words = text.split()
        chunks = []

        for i in range(0, len(words), size):
            chunk = " ".join(words[i:i + size])
            chunks.append(chunk)

        return chunks
        # ======================
    # CLEAR FILES
    # ======================
    def clear(self):
        self.index = FileFaissIndex()
        self._files_loaded = False
