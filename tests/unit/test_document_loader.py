import tempfile
import os
from pathlib import Path

import pytest

from src.knowledge.document_loader import DocumentLoader

@pytest.fixture
def sample_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        # create sample txt files
        file1 = dir_path / "doc1.txt"
        file1.write_text("Content of document one.", encoding="utf-8")
        file2 = dir_path / "subdir" / "doc2.txt"
        file2.parent.mkdir(parents=True, exist_ok=True)
        file2.write_text("Second document content.", encoding="utf-8")
        yield dir_path

def test_document_loader_loads_all_txt_files(sample_files):
    loader = DocumentLoader(sample_files)
    docs = loader.load_documents()
    # Should load both files
    assert len(docs) == 2
    contents = {doc["metadata"]["source"]: doc["content"] for doc in docs}
    assert contents["doc1.txt"] == "Content of document one."
    assert contents["doc2.txt"] == "Second document content."
