class TextChunker:
    """
    Splits long text into overlapping chunks.
    """

    def __init__(self, chunk_size=400, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text):
        if not text:
            return []

        words = text.split()
        chunks = []

        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            chunks.append(chunk_text)

            start = end - self.overlap
            if start < 0:
                start = 0

        return chunks
