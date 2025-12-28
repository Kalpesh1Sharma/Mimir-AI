import os
from PyPDF2 import PdfReader


class FileLoadError(Exception):
    pass


class FileLoader:
    """
    Loads text content from uploaded files.
    Supports TXT and PDF.
    """

    def load_files(self, file_paths):
        texts = []
        metadatas = []

        for path in file_paths:
            if not path or not os.path.exists(path):
                # Skip invalid paths safely
                continue

            try:
                text = self._load_single_file(path)
                if text.strip():
                    texts.append(text)
                    metadatas.append(
                        {
                            "source": os.path.basename(path)
                        }
                    )
            except Exception:
                # Never crash on bad file
                continue

        # 🔑 ALWAYS return two values
        return texts, metadatas

    def _load_single_file(self, file_path):
        if file_path.lower().endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        if file_path.lower().endswith(".pdf"):
            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                if page.extract_text():
                    pages.append(page.extract_text())
            return "\n".join(pages)

        raise FileLoadError(f"Unsupported file type: {file_path}")
