import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingModel:
    """
    Cloud-safe embedding model using TF-IDF.
    No external downloads. No transformers.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=512,
        )
        self._fitted = False

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        if not self._fitted:
            self.vectorizer.fit(texts)
            self._fitted = True

        vectors = self.vectorizer.transform(texts).toarray()
        return np.array(vectors)

