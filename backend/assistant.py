import re
import ast
import operator

from rag.embeddings import EmbeddingModel
from rag.retrieve import Retriever
from backend.file_qa.file_qa import FileQASystem
from backend.personas import PERSONAS


class MimirAssistant:
    def __init__(self):
        self.embedder = EmbeddingModel()
        self.retriever = Retriever(self.embedder)
        self.file_qa = FileQASystem()

    # ======================
    # PUBLIC ENTRY POINT
    # ======================
    def query(self, text, persona="default", mode="factual"):
        text = text.strip()

        # 1️⃣ Math fast path
        if self._is_simple_math(text):
            return {
                "answer": f"**{self._solve_math(text)}**",
                "sources": [],
                "confidence": 1.0,
                "metadata": {"tool": "math"},
            }

        # 2️⃣ File QA if files are uploaded
        if self.file_qa._files_loaded:
            return self.file_qa.answer(text)

        # 3️⃣ RAG / Persona response
        return self._handle_rag_query(text, persona, mode)

    # ======================
    # RAG HANDLER
    # ======================
    def _handle_rag_query(self, text, persona, mode):
        persona_prompt = PERSONAS.get(persona, PERSONAS["default"])

        # Creative mode → no grounding required
        if mode == "creative":
            return {
                "answer": persona_prompt["prefix"] + "\n\n" + text,
                "sources": [],
                "confidence": 0.6,
                "metadata": {"mode": "creative"},
            }

        # Factual mode → retrieval
        query_vec = self.embedder.embed(text)[0]
        results = self.retriever.retrieve(query_vec)

        if not results:
            return {
                "answer": "I couldn’t find reliable grounded information for this question.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {"mode": "factual"},
            }

        context = "\n\n".join([r["text"] for r in results])

        answer = (
            persona_prompt["prefix"]
            + "\n\n"
            + context[:1200]
        )

        return {
            "answer": answer,
            "sources": list({r["metadata"]["source"] for r in results}),
            "confidence": 0.9,
            "metadata": {"mode": "factual", "tool": "rag"},
        }

    # ======================
    # FILE INGESTION
    # ======================
    def ingest_files(self, file_paths):
        self.file_qa.ingest_files(file_paths)

    # ======================
    # MATH HELPERS
    # ======================
    def _is_simple_math(self, text: str) -> bool:
        return bool(re.fullmatch(r"[0-9\.\+\-\*/\(\) ]+", text))

    def _solve_math(self, expr: str):
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }

        def eval_node(node):
            if isinstance(node, ast.Num):
                return node.n
            if isinstance(node, ast.BinOp):
                return ops[type(node.op)](
                    eval_node(node.left),
                    eval_node(node.right),
                )
            raise ValueError("Unsupported expression")

        tree = ast.parse(expr, mode="eval")
        return eval_node(tree.body)
