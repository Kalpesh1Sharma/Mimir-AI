# backend/validators.py

from typing import Dict, Any, List
import re


class OutputValidator:
    """
    Enforces persona and mode constraints on assistant outputs.

    This validator distinguishes between:
    - grounded content (from retrieved sources)
    - ungrounded speculative generation
    """

    def validate(
        self,
        response: Dict[str, Any],
        persona: Dict[str, Any],
        mode: Dict[str, Any],
    ) -> Dict[str, Any]:

        answer = response.get("answer", "")
        sources = response.get("sources", [])

        # 1. Enforce mode-level rules
        validated = self._enforce_mode_rules(
            answer=answer,
            sources=sources,
            mode=mode,
        )

        # 2. Enforce persona-level rules
        validated = self._enforce_persona_rules(
            validated_response=validated,
            persona=persona,
        )

        return validated

    # ---------- MODE RULES ----------

    def _enforce_mode_rules(
        self,
        answer: str,
        sources: List[Any],
        mode: Dict[str, Any],
    ) -> Dict[str, Any]:

        hard_rules = mode.get("hard_rules", {})
        refusal_policy = mode.get("refusal_policy", {})

        # Factual mode: must have sources
        if hard_rules.get("requires_retrieval") and not sources:
            if refusal_policy.get("refuse_if_no_sources"):
                return self._refusal(
                    reason="No grounded sources available for a factual response."
                )

        # Factual mode: speculative language check
        # IMPORTANT:
        # Speculative language is allowed IF content is grounded in sources
        if not hard_rules.get("allow_speculation") and not sources:
            speculative_phrases = [
                "might be",
                "could be",
                "possibly",
                "i think",
                "it seems",
            ]
            for phrase in speculative_phrases:
                if phrase in answer.lower():
                    return self._refusal(
                        reason="Speculative language detected in factual mode."
                    )

        return {
            "answer": answer,
            "sources": sources,
            "confidence": 0.9 if sources else 0.0,
        }

    # ---------- PERSONA RULES ----------

    def _enforce_persona_rules(
        self,
        validated_response: Dict[str, Any],
        persona: Dict[str, Any],
    ) -> Dict[str, Any]:

        answer = validated_response.get("answer", "")
        hard_rules = persona.get("hard_rules", {})

        # Python-only persona: output must look like Python code
        if hard_rules.get("output_format") == "python":
            if not self._looks_like_python(answer):
                return self._refusal(
                    reason="Output violates Python-only persona constraints."
                )

        # No explanations persona rule
        if hard_rules.get("no_explanations"):
            explanation_markers = [
                "because",
                "this means",
                "explanation",
                "in summary",
            ]
            for marker in explanation_markers:
                if marker in answer.lower():
                    return self._refusal(
                        reason="Explanation detected where it is not allowed."
                    )

        # Emotional support: enforce empathy
        if hard_rules.get("empathetic_language_required"):
            if not self._contains_empathy(answer):
                return self._refusal(
                    reason="Empathetic language required but not detected."
                )

        return validated_response

    # ---------- HELPERS ----------

    def _refusal(self, reason: str) -> Dict[str, Any]:
        return {
            "answer": f"I’m unable to respond reliably: {reason}",
            "sources": [],
            "confidence": 0.0,
        }

    def _looks_like_python(self, text: str) -> bool:
        python_patterns = [
            r"^def\s+\w+\(",
            r"^class\s+\w+",
            r"import\s+\w+",
            r"for\s+\w+\s+in\s+",
            r"if\s+.+:",
        ]

        for pattern in python_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True

        return False

    def _contains_empathy(self, text: str) -> bool:
        empathy_markers = [
            "i’m sorry",
            "that sounds",
            "i understand",
            "it’s okay to feel",
            "you’re not alone",
        ]

        text = text.lower()
        return any(marker in text for marker in empathy_markers)
