from typing import List, Dict
from rag.embeddings import EmbeddingModel
import numpy as np


class FileFaissIndex:
    """
    Lightweight in-memory vector index (FAISS-like).
    """

    def __init__(self):
        self.embedder = EmbeddingModel()
        self.vectors = []
        self.texts = []
        self.metadatas = []

    def build(self, chunks: List[str], metadatas: List[Dict]):
        self.vectors = self.embedder.embed_batch(chunks)
        self.texts = chunks
        self.metadatas = metadatas

    def search(self, query: str, top_k: int = 3):
        if not self.vectors:
            return []

        query_vec = self.embedder.embed(query)[0]

        sims = np.dot(self.vectors, query_vec)

        top_idx = sims.argsort()[-top_k:][::-1]

        return [
            {
                "text": self.texts[i],
                "metadata": self.metadatas[i],
            }
            for i in top_idx
        ]
