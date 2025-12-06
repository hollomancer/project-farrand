from datetime import date
from typing import Dict, List

from src.agents.delegate_agent import DelegateAgent, DialogueTurn, ConversationContext
from src.validation.constraint_validator import ConstraintValidator
from src.orchestration.turn_taking_controller import TurnTakingController
from src.orchestration.global_state import GlobalState


class ConversationManager:
    def __init__(self, agents: Dict[str, DelegateAgent], validator: ConstraintValidator):
        self.agents = agents
        self.validator = validator
        self.history: List[DialogueTurn] = []
        # Initialize turn taking controller with available agent names
        self.turn_controller = TurnTakingController(list(agents.keys()))
        # Global state tracks topic, date, proposals, etc.
        self.global_state = GlobalState()
        # Sync initial topic and date with global state
        self.current_topic: str = self.global_state.current_topic
        self.current_date: date = self.global_state.current_date

    async def run_turn(self) -> DialogueTurn:
        # 1. Select next speaker using TurnTakingController
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
            # Placeholder for regeneration logic
            pass

        # 5. Record turn and update global state history
        self.history.append(turn)
        self.global_state.session_history.append({"speaker": speaker_name, "turn": turn})
        return turn

    def _select_speaker(self) -> str:
        """Delegate speaker selection to TurnTakingController."""
        return self.turn_controller.select_next()
