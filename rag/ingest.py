# rag/ingest.py

import os
import pickle
from typing import List, Dict

import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

from rag.embeddings import EmbeddingModel


class DocumentIngestor:
    """
    Handles document ingestion and FAISS index creation.
    """

    def __init__(
        self,
        data_dir: str = "data/raw",
        index_dir: str = "data/indices",
        chunk_size: int = 500,
        overlap: int = 100,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        if faiss is None:
            raise ImportError(
                "faiss not installed. Install with: pip install faiss-cpu"
            )

        self.data_dir = data_dir
        self.index_dir = index_dir
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedder = EmbeddingModel(embedding_model)

        os.makedirs(self.index_dir, exist_ok=True)

    def ingest_domain(self, domain: str) -> None:
        """
        Ingest all documents under a domain folder.
        """
        domain_path = os.path.join(self.data_dir, domain)

        if not os.path.exists(domain_path):
            raise FileNotFoundError(f"Domain folder not found: {domain_path}")

        texts, metadata = self._load_documents(domain_path)

        chunks, chunk_meta = self._chunk_texts(texts, metadata)

        embeddings = self.embedder.embed_batch(chunks)

        self._build_index(domain, embeddings, chunk_meta)

    # ---------- HELPERS ----------

    def _load_documents(self, domain_path: str):
        texts = []
        metadata = []

        for filename in os.listdir(domain_path):
            if not filename.endswith(".txt"):
                continue

            filepath = os.path.join(domain_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            texts.append(content)
            metadata.append({"source": filename})

        return texts, metadata

    def _chunk_texts(
        self,
        texts: List[str],
        metadata: List[Dict],
    ):
        chunks = []
        chunk_meta = []

        for text, meta in zip(texts, metadata):
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk = text[start:end]

                chunks.append(chunk)
                chunk_meta.append(
                    {
                        "text": chunk,
                        "source": meta["source"],
                        "start_char": start,
                        "end_char": end,
                    }
                )

                start += self.chunk_size - self.overlap

        return chunks, chunk_meta

    def _build_index(
        self,
        domain: str,
        embeddings: np.ndarray,
        metadata: List[Dict],
    ):
        dim = embeddings.shape[1]

        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)

        index_path = os.path.join(self.index_dir, f"{domain}.index")
        meta_path = os.path.join(self.index_dir, f"{domain}_meta.pkl")

        faiss.write_index(index, index_path)

        with open(meta_path, "wb") as f:
            pickle.dump(metadata, f)

        print(f"[✓] Built index for domain '{domain}' with {len(metadata)} chunks.")
