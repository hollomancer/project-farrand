from dataclasses import dataclass
from typing import Literal, List, Dict, Optional
from langchain_huggingface import HuggingFaceEndpoint

@dataclass
class DelegateProfile:
    name: str
    state: str
    role: str
    ideology: Literal["federalist", "anti-federalist", "moderate"]
    speaking_frequency: Literal["rare", "occasional", "frequent"]
    personality_traits: List[str]
    known_positions: Dict[str, str]  # topic -> stance
    rhetorical_style: str
    few_shot_examples: List[str]

@dataclass
class Source:
    text: str
    citation: str
    date: str
    author: Optional[str] = None

@dataclass
class DialogueTurn:
    speaker: str
    text: str
    citations: List[str]
    timestamp: str

@dataclass
class ConversationContext:
    topic: str
    recent_history: List[DialogueTurn]
    current_date: str

class DelegateAgent:
    def __init__(self, profile: DelegateProfile, llm: HuggingFaceEndpoint, rag_system):
        self.profile = profile
        self.llm = llm
        self.rag = rag_system
        self.conversation_history: List[DialogueTurn] = []

    async def generate_response(self, topic: str, context: ConversationContext) -> DialogueTurn:
        # 1. Retrieve relevant sources
        sources = await self.rag.retrieve(topic, self.profile.name)

        # 2. Build prompt with profile, context, and sources
        prompt = self._build_prompt(topic, context, sources)

        # 3. Generate response via HF Inference API
        response = await self.llm.ainvoke(prompt)

        # 4. Format with citations
        return self._format_turn(response, sources)

    def _build_prompt(self, topic: str, context: ConversationContext, sources: List[Source]) -> str:
        """Build instruction prompt for Llama 3.1."""
        system_prompt = f"""You are {self.profile.name}, a delegate from {self.profile.state} at the 1787 Constitutional Convention.

PERSONALITY: {self.profile.rhetorical_style}
IDEOLOGY: {self.profile.ideology}
KNOWN POSITIONS: {self.profile.known_positions}

RULES:
- Respond as {self.profile.name} would, using authentic 18th-century language and rhetoric
- Include citations to sources using【source】format
- Never reference events after September 17, 1787
- Stay true to your documented historical positions"""

        user_prompt = f"""HISTORICAL SOURCES:
{self._format_sources(sources)}

RECENT DEBATE:
{self._format_history(context.recent_history)}

Current topic: {topic}
Current date: {context.current_date}

Speak now as {self.profile.name}."""

        # Llama 3.1 chat format
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    def _format_sources(self, sources: List[Source]) -> str:
        return "\n".join([f"- {s.text} {s.citation}" for s in sources])

    def _format_history(self, history: List[DialogueTurn]) -> str:
        return "\n".join([f"{turn.speaker}: {turn.text}" for turn in history])

    def _format_turn(self, raw_response: str, sources: List[Source]) -> DialogueTurn:
        # Placeholder for actual formatting logic
        # In a real implementation, we would parse the citations and clean up the text
        from datetime import datetime
        return DialogueTurn(
            speaker=self.profile.name,
            text=raw_response.strip(),
            citations=[s.citation for s in sources], # Simplified
            timestamp=datetime.now().isoformat()
        )
