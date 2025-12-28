class Retriever:
    """
    Simple in-memory retriever over indexed documents.
    """

    def __init__(self, embedder):
        self.embedder = embedder
        self.documents = []
        self.metadatas = []

    def add_documents(self, texts, metadatas):
        for t, m in zip(texts, metadatas):
            self.documents.append(t)
            self.metadatas.append(m)

    def retrieve(self, query_vector, top_k=5):
        if not self.documents:
            return []

        # Since we are using TF-IDF, similarity is implicit
        results = []
        for text, meta in zip(self.documents, self.metadatas):
            results.append(
                {
                    "text": text,
                    "metadata": meta,
                }
            )

        return results[:top_k]
