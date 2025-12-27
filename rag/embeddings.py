from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class EmbeddingModel:
    """
    Lightweight embedding model using TF-IDF.
    Suitable for Streamlit Cloud (no downloads, no GPUs).
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=512
        )

        # Fit on a minimal corpus to initialize
        self._is_fitted = False

    def embed(self, texts):
        """
        Embed text(s) into vectors.
        Accepts str or list[str].
        """
        if isinstance(texts, str):
            texts = [texts]

        if not self._is_fitted:
            self.vectorizer.fit(texts)
            self._is_fitted = True

        vectors = self.vectorizer.transform(texts).toarray()
        return np.array(vectors)
