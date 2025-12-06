from datetime import date
from typing import Dict, List
from src.agents.delegate_agent import DelegateAgent, DialogueTurn, ConversationContext
from src.validation.constraint_validator import ConstraintValidator

class ConversationManager:
    def __init__(self, agents: Dict[str, DelegateAgent], validator: ConstraintValidator):
        self.agents = agents
        self.validator = validator
        self.history: List[DialogueTurn] = []
        self.current_topic: str = "General Debate"
        self.current_date: date = date(1787, 5, 25)

    async def run_turn(self) -> DialogueTurn:
        # 1. Select next speaker
        speaker_name = self._select_speaker()
        speaker = self.agents[speaker_name]

        # 2. Build context
        context = ConversationContext(
            topic=self.current_topic,
            recent_history=self.history[-10:],
            current_date=self.current_date.isoformat()
        )

        # 3. Generate response via HF Inference API
        turn = await speaker.generate_response(self.current_topic, context)

        # 4. Validate
        validation = self.validator.validate(turn)
        if not validation.is_valid:
            # In a real implementation, we would retry with feedback
            # turn = await self._regenerate_with_feedback(speaker, validation.feedback)
            pass

        # 5. Record and return
        self.history.append(turn)
        return turn

    def _select_speaker(self) -> str:
        """Simple speaker selection for MVP."""
        # Prioritize: relevance to topic > hasn't spoken recently > random
        # Respect speaking frequency constraints
        # For MVP, just pick the first available agent or random
        import random
        return random.choice(list(self.agents.keys()))
