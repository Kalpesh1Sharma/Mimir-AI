# api/deps.py

from backend.assistant import MimirAssistant

# Singleton assistant instance (session-based)
mimir_assistant = MimirAssistant()


def get_assistant() -> MimirAssistant:
    """
    Dependency provider for MimirAssistant.
    """
    return mimir_assistant
