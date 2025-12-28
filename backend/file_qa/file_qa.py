from backend.file_qa.loader import FileLoader
from backend.file_qa.chunker import TextChunker
from backend.file_qa.index import FileFaissIndex
from rag.embeddings import EmbeddingModel


class FileQASystem:
    """
    Handles file-based question answering.
    """

    def __init__(self):
        self.loader = FileLoader()
        self.chunker = TextChunker()

        # 🔑 Create ONE embedder instance
        self.embedder = EmbeddingModel()

        # 🔑 Pass embedder into FAISS index
        self.index = FileFaissIndex(self.embedder)

        self._files_loaded = False

    def ingest_files(self, file_paths):
        texts, metadatas = self.loader.load_files(file_paths)

        chunks = []
        chunk_metas = []

        for text, meta in zip(texts, metadatas):
            parts = self.chunker.chunk(text)
            for p in parts:
                chunks.append({"text": p})
                chunk_metas.append(meta)

        self.index.build(chunks, chunk_metas)
        self._files_loaded = True

    def answer(self, query):
        if not self._files_loaded:
            return {
                "answer": "No files uploaded yet.",
                "sources": [],
                "confidence": 0.0,
            }

        query_vec = self.embedder.embed(query)[0]
        results = self.index.search(query_vec, top_k=5)

        if not results:
            return {
                "answer": "I couldn’t find relevant information in the uploaded files.",
                "sources": [],
                "confidence": 0.3,
            }

        context = "\n".join([r.get("text", "") for r in results])

        answer = (
            "Based on the uploaded files:\n\n"
            + context[:800]
        )

        return {
            "answer": answer,
            "sources": ["uploaded_file"],
            "confidence": 0.9,
            "metadata": {"tool": "file_qa"},
        }

    def clear(self):
        self._files_loaded = False
        self.index = FileFaissIndex(self.embedder)
