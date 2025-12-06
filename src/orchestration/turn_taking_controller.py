from typing import List
import random

class TurnTakingController:
    """Simple controller for selecting the next speaker.

    For the MVP we implement a random selection from the available agents.
    Future versions may incorporate relevance scoring, speaking frequency, etc.
    """
    def __init__(self, agents: List[str]):
        self.agents = agents

    def select_next(self) -> str:
        return random.choice(self.agents)
