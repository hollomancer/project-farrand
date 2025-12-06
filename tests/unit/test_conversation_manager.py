import pytest
from datetime import date

from src.orchestration.conversation_manager import ConversationManager
from src.validation.constraint_validator import ConstraintValidator
from src.agents.delegate_agent import DialogueTurn, ConversationContext, DelegateProfile
from src.orchestration.global_state import GlobalState

# Simple dummy DelegateAgent
class DummyDelegateAgent:
    def __init__(self, name: str):
        self.profile = DelegateProfile(
            name=name,
            state="TestState",
            role="delegate",
            ideology="moderate",
            speaking_frequency="occasional",
            personality_traits=[],
            known_positions={},
            rhetorical_style="",
            few_shot_examples=[],
        )
        self.llm = None
        self.rag = None
        self.conversation_history = []

    async def generate_response(self, topic: str, context: ConversationContext) -> DialogueTurn:
        # Return a simple DialogueTurn
        return DialogueTurn(
            speaker=self.profile.name,
            text=f"Response on {topic}",
            citations=[],
            timestamp="2024-01-01T00:00:00"
        )

# Simple ConstraintValidator that always passes
class DummyValidator(ConstraintValidator):
    def __init__(self):
        super().__init__(anachronism_terms=set())

    def validate(self, turn: DialogueTurn):
        # Override to always return valid
        from src.validation.constraint_validator import ValidationResult
        return ValidationResult(is_valid=True, errors=[], feedback=None)

@pytest.fixture
def manager():
    agents = {"Alice": DummyDelegateAgent("Alice")}
    validator = DummyValidator()
    return ConversationManager(agents=agents, validator=validator)

def test_run_turn_updates_history_and_global_state(manager):
    # Run a turn
    import asyncio
    turn = asyncio.run(manager.run_turn())
    # Verify turn is a DialogueTurn and has correct speaker
    assert isinstance(turn, DialogueTurn)
    assert turn.speaker == "Alice"
    # History should contain the turn
    assert len(manager.history) == 1
    assert manager.history[0] == turn
    # Global state session_history should be updated
    assert len(manager.global_state.session_history) == 1
    entry = manager.global_state.session_history[0]
    assert entry["speaker"] == "Alice"
    assert entry["turn"] == turn

def test_initial_topic_and_date_sync_with_global_state(manager):
    # Ensure manager's topic and date match global state defaults
    assert manager.current_topic == manager.global_state.current_topic
    assert manager.current_date == manager.global_state.current_date
