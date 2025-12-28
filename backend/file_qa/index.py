import faiss
import numpy as np


class FileFaissIndex:
    """
    FAISS index for file-based question answering.
    Compatible with TF-IDF embeddings.
    """

    def __init__(self, embedder):
        self.embedder = embedder
        self.index = None
        self.metadatas = []

    def build(self, chunks, metadatas):
        """
        chunks: List[dict] with key 'text'
        metadatas: List[dict]
        """

        if not chunks:
            return

        # Extract raw text from chunks
        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedder.embed_batch(texts)

        if embeddings.size == 0:
            return

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype("float32"))

        self.metadatas = metadatas

    def search(self, query_vector, top_k=5):
        if self.index is None:
            return []

        distances, indices = self.index.search(
            query_vector.reshape(1, -1).astype("float32"),
            top_k,
        )

        results = []
        for idx in indices[0]:
            if idx < len(self.metadatas):
                results.append(self.metadatas[idx])

        return results
