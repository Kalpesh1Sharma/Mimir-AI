import re
import ast
import operator

from rag.embeddings import EmbeddingModel
from rag.retrieve import Retriever
from backend.file_qa.file_qa import FileQASystem
from backend.personas import PersonaManager


class MimirAssistant:
    def __init__(self):
        self.embedder = EmbeddingModel()
        self.retriever = Retriever(self.embedder)
        self.file_qa = FileQASystem()
        self.persona_manager = PersonaManager()

    # ======================
    # PUBLIC ENTRY POINT
    # ======================
    def query(self, text, persona="default", mode="factual"):
        text = text.strip()

        # 1️⃣ Math fast-path (NL + pure math)
        if self._contains_math(text):
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
                    pass  # fall through safely

        # 2️⃣ File QA if files uploaded
        if self.file_qa._files_loaded:
            return self.file_qa.answer(text)

        # 3️⃣ Persona + RAG
        persona_contract = self.persona_manager.load(persona)
        return self._handle_rag_query(text, persona_contract, mode)

    # ======================
    # RAG HANDLER
    # ======================
    def _handle_rag_query(self, text, persona_contract, mode):
        hard_rules = persona_contract.get("hard_rules", {})
        soft_prefs = persona_contract.get("soft_preferences", {})

        # Creative mode → no grounding
        if mode == "creative":
            return {
                "answer": self._format_creative(text, soft_prefs),
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

        answer = self._apply_persona_rules(
            context=context,
            hard_rules=hard_rules,
            soft_prefs=soft_prefs,
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
    # PERSONA LOGIC
    # ======================
    def _apply_persona_rules(self, context, hard_rules, soft_prefs):
        # Python-only persona
        if hard_rules.get("output_format") == "python":
            return context

        # Emotional support
        if hard_rules.get("empathetic_language_required"):
            return (
                "I hear you. You’re not alone.\n\n"
                + context
            )

        # Corporate
        if hard_rules.get("formal_language"):
            return "Summary:\n\n" + context

        return context

    def _format_creative(self, text, soft_prefs):
        tone = soft_prefs.get("tone", "neutral")
        if tone == "narrative":
            return f"Let me tell this as a story:\n\n{text}"
        return text

    # ======================
    # MATH HELPERS
    # ======================
    def _contains_math(self, text: str) -> bool:
        return bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", text))

    def _extract_math_expression(self, text: str) -> str:
        """
        Extracts math from NL text.
        Examples:
        - 'what is 3+2' → '3+2'
        - 'calculate (4+6)*2' → '(4+6)*2'
        """
        match = re.search(r"([\d\.\+\-\*/\(\) ]+)", text)
        return match.group(1).strip() if match else ""

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
