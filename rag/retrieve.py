# rag/retrieve.py

from typing import List, Dict, Any
import os
import pickle
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None


class FaissRetriever:
    """
    FAISS-based similarity retriever with strict validation.
    """

    def __init__(self, index_dir: str = "data/indices"):
        if faiss is None:
            raise ImportError(
                "faiss not installed. Install with: pip install faiss-cpu"
            )

        self.index_dir = index_dir
        self.indices: Dict[str, faiss.Index] = {}
        self.metadata: Dict[str, List[Dict[str, Any]]] = {}

    def load_domain(self, domain: str) -> None:
        """
        Load FAISS index and metadata for a domain.
        """
        index_path = os.path.join(self.index_dir, f"{domain}.index")
        meta_path = os.path.join(self.index_dir, f"{domain}_meta.pkl")

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found: {index_path}")

        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata file not found: {meta_path}")

        index = faiss.read_index(index_path)

        with open(meta_path, "rb") as f:
            meta = pickle.load(f)

        if index.ntotal != len(meta):
            raise ValueError(
                f"Index/vector count mismatch for domain '{domain}': "
                f"{index.ntotal} vectors vs {len(meta)} metadata entries"
            )

        self.indices[domain] = index
        self.metadata[domain] = meta

        print(f"[✓] Loaded domain '{domain}' with {index.ntotal} vectors")

    def retrieve(
        self,
        query_vector: np.ndarray,
        domain: str = "general",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant chunks for a query vector.
        """

        if domain not in self.indices:
            self.load_domain(domain)

        index = self.indices[domain]
        meta = self.metadata[domain]

        if index.ntotal == 0:
            return []

        query_vector = np.expand_dims(query_vector, axis=0)

        scores, indices = index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue

            item = meta[idx].copy()
            item["score"] = float(score)
            results.append(item)

        return results
