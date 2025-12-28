from typing import List, Dict, Any

from backend.file_qa.loader import FileLoader
from backend.file_qa.chunker import TextChunker
from backend.file_qa.index import FileFaissIndex


class FileQASystem:
    """
    Handles file-based question answering.

    Flow:
    Files → Load → Chunk → Embed → Index → Retrieve → Answer
    """

    def __init__(self):
        self.loader = FileLoader()
        self.chunker = TextChunker()
        self.index = FileFaissIndex()

        self._files_loaded = False

    # ======================
    # PUBLIC CONTRACTS
    # ======================
    def has_files(self) -> bool:
        """
        Public, safe check used by assistant/router.
        """
        return self._files_loaded

    # ======================
    # FILE INGESTION
    # ======================
    def ingest_files(self, file_paths: List[str]):
        """
        Ingest user-uploaded files into vector index.
        """
        texts, metadatas = self.loader.load_files(file_paths)

        if not texts:
            return

        all_chunks = []
        all_metadata = []

        for text, meta in zip(texts, metadatas):
            chunks = self.chunker.chunk(text)
            all_chunks.extend(chunks)
            all_metadata.extend([meta] * len(chunks))

        if not all_chunks:
            return

        self.index.build(all_chunks, all_metadata)
        self._files_loaded = True

    # ======================
    # QUESTION ANSWERING
    # ======================
    def answer(self, query: str) -> Dict[str, Any]:
        """
        Answer questions strictly from uploaded files.
        """
        if not self._files_loaded:
            return {
                "answer": "No files have been uploaded yet.",
                "sources": [],
                "confidence": 0.0,
                "metadata": {"tool": "file_qa"},
            }

        results = self.index.search(query)

        if not results:
            return {
                "answer": "I couldn’t find relevant information in the uploaded files.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {"tool": "file_qa"},
            }

        context = "\n\n".join(r["text"] for r in results)

        sources = list({r["metadata"].get("source", "uploaded_file") for r in results})

        return {
            "answer": context,
            "sources": sources,
            "confidence": 0.85,
            "metadata": {"tool": "file_qa"},
        }
