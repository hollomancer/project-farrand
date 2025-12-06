import os
from pathlib import Path
from typing import List, Dict

class DocumentLoader:
    """Simple loader that reads all .txt files from a given directory and returns
    a list of documents with basic metadata.

    Each document is represented as a dict with keys:
        - content: str, the raw text of the file
        - metadata: dict, containing at least 'source' (filename) and 'path'
    """

    def __init__(self, source_dir: str | os.PathLike):
        self.source_dir = Path(source_dir)
        if not self.source_dir.is_dir():
            raise ValueError(f"Source directory does not exist: {self.source_dir}")

    def load_documents(self) -> List[Dict[str, object]]:
        docs = []
        for file_path in self.source_dir.rglob("*.txt"):
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                # Skip unreadable files but continue processing others
                continue
            docs.append({
                "content": content,
                "metadata": {
                    "source": file_path.name,
                    "path": str(file_path),
                },
            })
        return docs
