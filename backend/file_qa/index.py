import faiss
import numpy as np


class FileFaissIndex:
    def __init__(self, embedder):
        self.embedder = embedder
        self.index = None
        self.texts = []
        self.metadatas = []

    def build(self, chunks, metadatas):
        self.texts = [c["text"] for c in chunks]
        self.metadatas = metadatas

        embeddings = self.embedder.embed_batch(self.texts)
        vectors = np.array(embeddings).astype("float32")

        dim = vectors.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(vectors)

    def search(self, query_vector, top_k=5):
        if self.index is None:
            return []

        D, I = self.index.search(
            np.array([query_vector]).astype("float32"),
            top_k
        )

        results = []
        for idx in I[0]:
            if idx < len(self.texts):
                results.append(
                    {
                        "text": self.texts[idx],
                        "metadata": self.metadatas[idx],
                    }
                )

        return results
