import re
import ast
import operator
from typing import Dict, Any

from rag.embeddings import EmbeddingModel
from rag.retrieve import Retriever
from backend.file_qa.file_qa import FileQASystem
from backend.personas import PersonaManager
from backend.web_search import WebSearchQA


class MimirAssistant:
    def __init__(self):
        self.embedder = EmbeddingModel()
        self.retriever = Retriever(self.embedder)
        self.file_qa = FileQASystem()
        self.persona_manager = PersonaManager()
        self.web_search = WebSearchQA()

    # ======================
    # PUBLIC ENTRY POINT
    # ======================
    def query(self, text: str, persona: str = "default", mode: str = "factual") -> Dict[str, Any]:
        text = text.strip()

        # 1️⃣ Math fast-path (NO embeddings, NO retrieval)
        expr = self._extract_math_expression(text)
        if expr:
            try:
                return {
                    "answer": f"**{self._solve_math(expr)}**",
                    "sources": [],
                    "confidence": 1.0,
                    "metadata": {"tool": "math"},
                }
            except Exception:
                pass

        # 2️⃣ Uploaded file QA (highest priority after math)
        if self.file_qa.has_files():
            return self.file_qa.answer(text)

        # 3️⃣ Web search fallback (FACTUAL QUESTIONS)
        web_result = self.web_search.answer(text)
        if web_result.get("confidence", 0) >= 0.5:
            return web_result

        # 4️⃣ Persona + RAG
        persona_contract = self.persona_manager.load(persona)
        return self._handle_rag_query(text, persona_contract, mode)

    # ======================
    # RAG HANDLER
    # ======================
    def _handle_rag_query(self, text: str, persona_contract: Dict[str, Any], mode: str):
        hard_rules = persona_contract.get("hard_rules", {})
        soft_prefs = persona_contract.get("soft_preferences", {})

        # Creative mode = NO retrieval
        if mode == "creative":
            return {
                "answer": self._format_creative(text, soft_prefs),
                "sources": [],
                "confidence": 0.6,
                "metadata": {"mode": "creative"},
            }

        # Safe embed (guard against empty vocab)
        try:
            query_vec = self.embedder.embed(text)[0]
        except Exception:
            return {
                "answer": "I couldn’t find reliable grounded information for this question.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {"mode": "factual"},
            }

        results = self.retriever.retrieve(query_vec)

        if not results:
            return {
                "answer": "I couldn’t find reliable grounded information for this question.",
                "sources": [],
                "confidence": 0.3,
                "metadata": {"mode": "factual"},
            }

        context = "\n\n".join(r["text"] for r in results)

        answer = self._apply_persona_rules(
            context=context,
            hard_rules=hard_rules,
            soft_prefs=soft_prefs,
        )

        return {
            "answer": answer,
            "sources": list({r["metadata"].get("source", "rag") for r in results}),
            "confidence": 0.9,
            "metadata": {"mode": "factual", "tool": "rag"},
        }

    # ======================
    # FILE INGESTION
    # ======================
    def ingest_files(self, file_paths):
        self.file_qa.ingest_files(file_paths)

    # ======================
    # PERSONA LOGIC
    # ======================
    def _apply_persona_rules(self, context: str, hard_rules: Dict[str, Any], soft_prefs: Dict[str, Any]) -> str:
        if hard_rules.get("output_format") == "python":
            return context

        if hard_rules.get("empathetic_language_required"):
            return "I hear you.\n\n" + context

        if hard_rules.get("formal_language"):
            return "Summary:\n\n" + context

        return context

    def _format_creative(self, text: str, soft_prefs: Dict[str, Any]) -> str:
        if soft_prefs.get("tone") == "narrative":
            return f"Let me tell this as a story:\n\n{text}"
        return text

    # ======================
    # MATH
    # ======================
    def _extract_math_expression(self, text: str) -> str:
        matches = re.findall(
            r"\(?\d+(?:\.\d+)?(?:\s*[\+\-\*/]\s*\(?\d+(?:\.\d+)?\)?)+",
            text,
        )
        return matches[0] if matches else ""

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
