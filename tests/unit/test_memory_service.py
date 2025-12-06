import pytest
from datetime import datetime, timedelta

from src.memory.service import MemoryService

@pytest.fixture
def service():
    return MemoryService()

def test_add_and_recent_memory(service):
    # Add three entries with slight time differences
    service.add_memory("Madison", "First entry")
    service.add_memory("Madison", "Second entry")
    service.add_memory("Madison", "Third entry")
    recent = service.recent("Madison", limit=2)
    # Should return the most recent two entries (Third, Second)
    assert len(recent) == 2
    assert recent[0].content == "Third entry"
    assert recent[1].content == "Second entry"

def test_memory_by_topic(service):
    service.add_memory("Hamilton", "Economy speech", metadata={"topic": "economy"})
    service.add_memory("Hamilton", "Foreign policy speech", metadata={"topic": "foreign"})
    service.add_memory("Hamilton", "Another economy note", metadata={"topic": "economy"})
    econ = service.by_topic("Hamilton", "economy")
    assert len(econ) == 2
    topics = {e.metadata["topic"] for e in econ}
    assert topics == {"economy"}
