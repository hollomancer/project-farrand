from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Any

@dataclass
class Proposal:
    description: str
    votes: Dict[str, str]  # delegate name -> vote (e.g., "yes", "no")
    outcome: str | None = None

@dataclass
class GlobalState:
    """Tracks overall session state for the convention simulation."""
    proposals: List[Proposal] = field(default_factory=list)
    current_topic: str = "General Debate"
    current_date: date = date(1787, 5, 25)
    session_history: List[Dict[str, Any]] = field(default_factory=list)

    def add_proposal(self, proposal: Proposal) -> None:
        self.proposals.append(proposal)

    def advance_topic(self, new_topic: str) -> None:
        self.current_topic = new_topic
        # Simple date increment for demo purposes
        self.current_date = date(self.current_date.year, self.current_date.month, self.current_date.day + 1)
