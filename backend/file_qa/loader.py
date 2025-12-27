# backend/file_qa/loader.py

"""
File Loader for Mimir File Q&A (Session-based)

Responsibilities:
- Accept uploaded files (PDF / TXT)
- Extract clean text
- Fail safely with clear errors
- NO persistence (session-only)
"""

from typing import List
from pathlib import Path

import io

# PDF support
from PyPDF2 import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".pdf"}


class FileLoadError(Exception):
    """Raised when a file cannot be loaded or parsed safely."""
    pass


class FileLoader:
    """
    Loads user-uploaded files and extracts raw text.
    """

    def __init__(self, max_file_size_mb: int = 10):
        """
        :param max_file_size_mb: Safety limit per file
        """
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    # --------------------------------------------------

    def load_files(self, file_paths: List[str]) -> List[str]:
        """
        Load multiple files and return extracted text blocks.

        :param file_paths: list of file paths
        :return: list of extracted text strings
        """
        texts = []

        for path in file_paths:
            text = self._load_single_file(path)
            if text.strip():
                texts.append(text)

        if not texts:
            raise FileLoadError("No readable text found in uploaded files.")

        return texts

    # --------------------------------------------------

    def _load_single_file(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileLoadError(f"File not found: {file_path}")

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise FileLoadError(
                f"Unsupported file type: {path.suffix}. "
                f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        file_size = path.stat().st_size
        if file_size > self.max_file_size_bytes:
            raise FileLoadError(
                f"File '{path.name}' exceeds size limit "
                f"({file_size / (1024*1024):.2f} MB)."
            )

        if path.suffix.lower() == ".txt":
            return self._load_txt(path)

        if path.suffix.lower() == ".pdf":
            return self._load_pdf(path)

        # Should never reach here
        raise FileLoadError(f"Unhandled file type: {path.suffix}")

    # --------------------------------------------------

    def _load_txt(self, path: Path) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            raise FileLoadError(f"Failed to read TXT file '{path.name}': {e}")

    # --------------------------------------------------

    def _load_pdf(self, path: Path) -> str:
        try:
            text_parts = []

            with open(path, "rb") as f:
                reader = PdfReader(f)

                if not reader.pages:
                    raise FileLoadError(f"PDF '{path.name}' contains no pages.")

                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            return "\n".join(text_parts)

        except Exception as e:
            raise FileLoadError(f"Failed to read PDF '{path.name}': {e}")
