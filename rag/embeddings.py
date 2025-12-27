# rag/embeddings.py

from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class EmbeddingModel:
    """
    Wrapper around sentence embedding models.

    This layer is intentionally thin so models can be swapped
    without affecting downstream retrieval logic.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> np.ndarray:
        """
        Embed a single text string.
        """
        return self.model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Embed a batch of texts.
        """
        return self.model.encode(texts, normalize_embeddings=True)
