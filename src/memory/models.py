from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class MemoryEntry:
    """A single memory entry stored for a delegate.

    Attributes:
        content: The text content of the memory.
        timestamp: When the entry was created.
        metadata: Additional key/value metadata (e.g., topic, tags).
    """
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class MemoryModel:
    """Container for a delegate's memory.

    Stores a list of MemoryEntry objects. Provides simple retrieval based on
    timestamp ordering and optional metadata filtering.
    """
    entries: List[MemoryEntry]

    def add_entry(self, content: str, metadata: Dict[str, Any] = None) -> None:
        if metadata is None:
            metadata = {}
        self.entries.append(MemoryEntry(content=content, timestamp=datetime.utcnow(), metadata=metadata))

    def recent(self, limit: int = 10) -> List[MemoryEntry]:
        # Return the most recent entries up to limit
        return sorted(self.entries, key=lambda e: e.timestamp, reverse=True)[:limit]

    def filter_by_topic(self, topic: str) -> List[MemoryEntry]:
        return [e for e in self.entries if e.metadata.get("topic") == topic]
