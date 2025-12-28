import re
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingModel:
    """
    Simple TF-IDF embedding model with safety checks.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            token_pattern=r"(?u)\b\w+\b"
        )

    def _has_valid_tokens(self, text: str) -> bool:
        # Check if text has at least one alphabetic token
        return bool(re.search(r"[a-zA-Z]", text))

    def embed(self, text: str):
        if not text or not self._has_valid_tokens(text):
            # Return a dummy vector instead of crashing
            return [[0.0]]

        self.vectorizer.fit([text])
        vec = self.vectorizer.transform([text]).toarray()
        return vec.tolist()

    def embed_batch(self, texts):
        valid_texts = [t for t in texts if self._has_valid_tokens(t)]

        if not valid_texts:
            return [[0.0] for _ in texts]

        self.vectorizer.fit(valid_texts)
        vectors = self.vectorizer.transform(texts).toarray()
        return vectors.tolist()
