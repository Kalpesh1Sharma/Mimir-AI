# backend/modes.py

from typing import Dict, Any


class ModeManager:
    """
    Manages assistant interaction modes.

    Modes define how strictly the assistant must adhere
    to grounded information vs creative generation.
    """

    def __init__(self):
        self._modes = self._load_modes()

    def load(self, mode_name: str) -> Dict[str, Any]:
        """
        Load a mode contract by name.
        Falls back to 'factual' if mode is unknown.
        """
        return self._modes.get(mode_name, self._modes["factual"])

    def _load_modes(self) -> Dict[str, Dict[str, Any]]:
        """
        Define all supported modes here.
        """

        return {
            "factual": {
                "hard_rules": {
                    "requires_retrieval": True,
                    "allow_speculation": False,
                    "must_cite_sources": True,
                },
                "refusal_policy": {
                    "refuse_if_no_sources": True,
                    "refuse_if_low_confidence": True,
                },
                "metadata": {
                    "label": "Factual Mode",
                    "description": "Grounded responses only. Refuses to answer without evidence.",
                },
            },

            "creative": {
                "hard_rules": {
                    "requires_retrieval": False,
                    "allow_speculation": True,
                    "must_cite_sources": False,
                },
                "refusal_policy": {
                    "refuse_if_no_sources": False,
                },
                "metadata": {
                    "label": "Creative Mode",
                    "description": "Allows fictional, speculative, and imaginative responses.",
                },
            },
        }
