from typing import Dict, List
from .models import MemoryModel, MemoryEntry

class MemoryService:
    """Service managing memory for multiple delegates.

    For the MVP we keep an in‑memory dictionary of ``MemoryModel`` instances keyed by
    delegate name. The service provides methods to add entries and retrieve recent
    memories with optional topic filtering. A simple recency weighting is applied
    by returning the most recent entries first.
    """

    def __init__(self):
        self._stores: Dict[str, MemoryModel] = {}

    def _get_store(self, delegate: str) -> MemoryModel:
        if delegate not in self._stores:
            self._stores[delegate] = MemoryModel(entries=[])
        return self._stores[delegate]

    def add_memory(self, delegate: str, content: str, metadata: Dict = None) -> None:
        """Add a memory entry for ``delegate``.

        Args:
            delegate: Identifier of the delegate (e.g., "Madison").
            content: The textual memory.
            metadata: Optional dict of additional information (topic, tags, etc.).
        """
        store = self._get_store(delegate)
        store.add_entry(content, metadata or {})

    def recent(self, delegate: str, limit: int = 10) -> List[MemoryEntry]:
        """Return the most recent ``limit`` entries for ``delegate``."""
        store = self._get_store(delegate)
        return store.recent(limit)

    def by_topic(self, delegate: str, topic: str) -> List[MemoryEntry]:
        """Retrieve entries for ``delegate`` that match a given ``topic``."""
        store = self._get_store(delegate)
        return store.filter_by_topic(topic)

    # Placeholder for future vector‑based retrieval; for now we expose the API
    def retrieve(self, delegate: str, query: str, limit: int = 5) -> List[MemoryEntry]:
        """MVP retrieval – simply returns recent entries.
        In a full implementation this would embed ``query`` and perform a vector
        similarity search against stored memories.
        """
        return self.recent(delegate, limit)
