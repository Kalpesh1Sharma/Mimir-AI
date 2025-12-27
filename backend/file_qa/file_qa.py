# backend/file_qa/file_qa.py

"""
File Q&A Orchestrator for Mimir (Session-based)

Responsibilities:
- Load uploaded files
- Chunk extracted text
- Build a session-scoped FAISS index
- Answer questions using uploaded documents only
"""

from typing import List, Dict, Any, Optional

from backend.file_qa.loader import FileLoader, FileLoadError
from backend.file_qa.chunker import TextChunker
from backend.file_qa.index import FileFaissIndex

from backend.llm import LLMClient


class FileQASystem:
    """
    End-to-end File Upload Q&A pipeline.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100,
    ):
        self.loader = FileLoader()
        self.chunker = TextChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )
        self.index = FileFaissIndex()
        self.llm = LLMClient(provider="mock")

        self._files_loaded = False

    # --------------------------------------------------

    def ingest_files(self, file_paths: List[str]):
        """
        Load and index uploaded files for this session.

        :param file_paths: List of file paths
        """
        # 1️⃣ Load raw text
        texts = self.loader.load_files(file_paths)

        # 2️⃣ Chunk text
        chunks = self.chunker.chunk_multiple_texts(texts)

        if not chunks:
            raise FileLoadError("No usable text chunks created from uploaded files.")

        # 3️⃣ Optional metadata (can expand later)
        metadatas = [{"source": "uploaded_file"} for _ in chunks]

        # 4️⃣ Build FAISS index
        self.index.build(chunks, metadatas)

        self._files_loaded = True

    # --------------------------------------------------

    def answer(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answer a question using uploaded files only.

        :param query: User question
        :param top_k: Number of chunks to retrieve
        """
        if not self._files_loaded:
            return {
                "answer": "No files have been uploaded for this session.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {
                    "note": "no_files_uploaded",
                },
            }

        # 1️⃣ Retrieve relevant chunks
        results = self.index.search(query, top_k=top_k)

        if not results:
            return {
                "answer": "I couldn’t find relevant information in the uploaded files.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {
                    "note": "no_relevant_chunks",
                },
            }

        # 2️⃣ Prepare context for LLM
        context_chunks = [
            {
                "text": r["text"],
                "source": r["metadata"].get("source", "uploaded_file"),
            }
            for r in results
        ]

        # 3️⃣ Synthesize answer
        answer = self.llm.synthesize(
            query=query,
            chunks=context_chunks,
            mode="factual",
        )

        return {
            "answer": answer,
            "sources": list({c["source"] for c in context_chunks}),
            "confidence": 0.9,
            "metadata": {
                "tool": "file_qa",
            },
        }

    # --------------------------------------------------

    def clear(self):
        """
        Clear session state (files + index).
        """
        self.index.clear()
        self._files_loaded = False
