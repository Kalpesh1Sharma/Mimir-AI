import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingModel:
    """
    Cloud-safe embedding model using TF-IDF.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=512,
        )
        self._fitted = False

    def embed(self, text: str):
        if not self._fitted:
            self.vectorizer.fit([text])
            self._fitted = True
        return self.vectorizer.transform([text]).toarray()

    def embed_batch(self, texts):
        if not texts:
            return np.array([])

        if not self._fitted:
            self.vectorizer.fit(texts)
            self._fitted = True

        return self.vectorizer.transform(texts).toarray()
