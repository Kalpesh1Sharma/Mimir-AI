# backend/file_qa/chunker.py

"""
Text Chunker for Mimir File Q&A (Session-based)

Responsibilities:
- Take raw text from uploaded files
- Split into overlapping chunks
- Preserve context across chunks
- Prepare text for embedding & FAISS indexing
"""

from typing import List


class TextChunker:
    """
    Splits text into overlapping chunks.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100,
    ):
        """
        :param chunk_size: Number of characters per chunk
        :param overlap: Number of overlapping characters between chunks
        """
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    # --------------------------------------------------

    def chunk_text(self, text: str) -> List[str]:
        """
        Split a single text string into overlapping chunks.

        :param text: Raw input text
        :return: List of text chunks
        """
        if not text or not text.strip():
            return []

        # Normalize whitespace
        text = self._normalize(text)

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            # Move window with overlap
            start = end - self.overlap

            if start < 0:
                start = 0

        return chunks

    # --------------------------------------------------

    def chunk_multiple_texts(self, texts: List[str]) -> List[str]:
        """
        Chunk multiple documents into a single list of chunks.

        :param texts: List of raw text documents
        :return: List of all chunks
        """
        all_chunks = []

        for text in texts:
            chunks = self.chunk_text(text)
            all_chunks.extend(chunks)

        return all_chunks

    # --------------------------------------------------

    def _normalize(self, text: str) -> str:
        """
        Normalize whitespace and clean text slightly.
        """
        # Replace multiple newlines with space
        text = text.replace("\r", " ").replace("\n", " ")

        # Collapse extra spaces
        while "  " in text:
            text = text.replace("  ", " ")

        return text.strip()
