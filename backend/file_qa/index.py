# backend/file_qa/index.py

"""
Session-based FAISS index for File Upload Q&A.

Responsibilities:
- Embed text chunks
- Build an in-memory FAISS index
- Perform similarity search over uploaded files
- NO persistence (cleared when session ends)
"""

from typing import List, Dict, Any
import faiss
import numpy as np

from rag.embeddings import EmbeddingModel


class FileFaissIndex:
    """
    In-memory FAISS index for uploaded files (session-scoped).
    """

    def __init__(self):
        self.embedder = EmbeddingModel()

        self.index = None
        self.text_chunks: List[str] = []
        self.metadata: List[Dict[str, Any]] = []

        self.embedding_dim = None

    # --------------------------------------------------

    def build(self, chunks: List[str], metadatas: List[Dict[str, Any]] = None):
        """
        Build a FAISS index from text chunks.

        :param chunks: List of text chunks
        :param metadatas: Optional metadata per chunk
        """
        if not chunks:
            raise ValueError("No chunks provided to build File FAISS index.")

        embeddings = self.embedder.embed_batch(chunks)
        embeddings = np.array(embeddings).astype("float32")

        self.embedding_dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings)

        self.text_chunks = chunks
        self.metadata = metadatas or [{} for _ in chunks]

    # --------------------------------------------------

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search uploaded file chunks for relevant context.

        :param query: User query
        :param top_k: Number of chunks to retrieve
        :return: List of matched chunks with metadata
        """
        if self.index is None:
            return []

        query_vec = self.embedder.embed(query)
        query_vec = np.array([query_vec]).astype("float32")

        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self.text_chunks):
                continue

            results.append({
                "text": self.text_chunks[idx],
                "metadata": self.metadata[idx],
            })

        return results

    # --------------------------------------------------

    def clear(self):
        """
        Clear the index (end of session).
        """
        self.index = None
        self.text_chunks = []
        self.metadata = []
        self.embedding_dim = None
