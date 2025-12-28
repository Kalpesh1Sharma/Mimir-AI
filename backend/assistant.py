import re
import ast
import operator

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
    def query(self, text, persona="default", mode="factual"):
        text = text.strip()

        # 1️⃣ Math fast-path
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

        # 2️⃣ File QA
        if self.file_qa.has_files():
            result = self.file_qa.answer(text)
            if result and result.get("answer"):
                return result

        # 3️⃣ Persona + RAG
        persona_contract = self.persona_manager.load(persona)
        rag_result = self._handle_rag_query(text, persona_contract, mode)

        if rag_result["confidence"] >= 0.6:
            return rag_result

        # 4️⃣ 🌍 WEB SEARCH FALLBACK (THIS FIXES EVERYTHING)
        try:
            web = self.web_search.search(text)
            if web:
                return web
        except Exception:
            pass

        # 5️⃣ Final refusal (very rare now)
        return {
            "answer": "I couldn’t find reliable information for this question.",
            "sources": [],
            "confidence": 0.2,
            "metadata": {"tool": "fallback"},
        }

    # ======================
    # RAG HANDLER
    # ======================
    def _handle_rag_query(self, text, persona_contract, mode):
        hard_rules = persona_contract.get("hard_rules", {})
        soft_prefs = persona_contract.get("soft_preferences", {})

        if mode == "creative":
            return {
                "answer": self._format_creative(text, soft_prefs),
                "sources": [],
                "confidence": 0.6,
                "metadata": {"mode": "creative"},
            }

        query_vec = self.embedder.embed(text)[0]
        results = self.retriever.retrieve(query_vec)

        if not results:
            return {
                "answer": "",
                "sources": [],
                "confidence": 0.0,
                "metadata": {"mode": "factual"},
            }

        context = "\n\n".join([r["text"] for r in results])

        answer = self._apply_persona_rules(
            context=context,
            hard_rules=hard_rules,
            soft_prefs=soft_prefs,
        )

        return {
            "answer": answer,
            "sources": list({r["metadata"]["source"] for r in results}),
            "confidence": 0.9,
            "metadata": {"tool": "rag"},
        }

    # ======================
    # FILE INGESTION
    # ======================
    def ingest_files(self, file_paths):
        self.file_qa.ingest_files(file_paths)

    # ======================
    # PERSONA LOGIC
    # ======================
    def _apply_persona_rules(self, context, hard_rules, soft_prefs):
        if hard_rules.get("empathetic_language_required"):
            return "I hear you.\n\n" + context

        if hard_rules.get("formal_language"):
            return "Summary:\n\n" + context

        return context

    def _format_creative(self, text, soft_prefs):
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
