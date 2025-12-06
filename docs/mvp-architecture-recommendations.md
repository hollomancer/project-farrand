# MVP Architecture Recommendations

## Executive Summary

The Constitutional Convention Simulation System is an ambitious multi-agent LLM project. The full specification includes 55 delegate agents, 51 correctness properties, and a 31-phase implementation plan. This document provides recommendations for a Minimum Viable Product (MVP) that demonstrates core value while managing complexity.

**MVP Goal**: Demonstrate historically-grounded, multi-agent dialogue among key Constitutional Convention delegates with RAG-based citation and basic consistency validation.

---

## What to Build in MVP vs. Defer

### MVP Scope (Phase 1)

| Component | MVP Scope | Full Scope |
|-----------|-----------|------------|
| **Delegates** | 5-7 key figures | 55 delegates |
| **Knowledge Base** | 50-100 curated docs | 150+ documents |
| **Memory System** | Simple per-agent context | Vector-based semantic memory |
| **Validation** | Basic anachronism filter | Multi-tier validation + secondary LLM |
| **Testing** | 3-5 episode fixtures | 15-20+ episode tests |
| **Turn-Taking** | Simple round-robin + relevance | Sophisticated topic-aware selection |
| **Debate Topics** | 2-3 core debates | Full Convention schedule |

### MVP Delegate Selection (7 Delegates)

Focus on delegates who represent diverse viewpoints and have substantial documentation:

1. **James Madison** (VA) - Federalist, frequent speaker, architect
2. **Alexander Hamilton** (NY) - Federalist, strong national government
3. **George Mason** (VA) - Anti-Federalist, Bill of Rights advocate
4. **Roger Sherman** (CT) - Moderate, Connecticut Compromise
5. **Gouverneur Morris** (PA) - Federalist, stylistically distinctive
6. **Benjamin Franklin** (PA) - Elder statesman, consensus builder
7. **George Washington** (VA) - President, rarely speaks (control case)

### MVP Debate Topics (3 Topics)

1. **Representation** (Virginia Plan vs New Jersey Plan)
2. **Executive Power** (Single vs plural executive, term length)
3. **Federal vs State Authority** (Supremacy, veto powers)

---

## Recommended MVP Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MVP Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   CLI/API    │────▶│ Conversation │────▶│   Output     │    │
│  │  Interface   │     │   Manager    │     │  Formatter   │    │
│  └──────────────┘     └──────┬───────┘     └──────────────┘    │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Delegate   │     │     RAG      │     │  Constraint  │    │
│  │    Agents    │◀───▶│    System    │     │  Validator   │    │
│  │   (7 total)  │     │              │     │              │    │
│  └──────────────┘     └──────┬───────┘     └──────────────┘    │
│                              │                                   │
│                       ┌──────▼───────┐                          │
│                       │    Vector    │                          │
│                       │   Database   │                          │
│                       │  (Pinecone)  │                          │
│                       └──────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Recommendations for MVP

### Primary Stack

| Component | Recommendation | Rationale |
|-----------|----------------|-----------|
| **Language** | Python 3.11+ | Richer LLM ecosystem, faster prototyping |
| **LLM Provider** | Hugging Face Inference API | Cost-effective, open models, good free tier |
| **LLM Model** | `mistralai/Mixtral-8x7B-Instruct-v0.1` | Strong instruction-following, 32k context |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Fast, high-quality, free on HF |
| **Vector DB** | Pinecone (Starter/Free tier) | Managed cloud, generous free tier |
| **Framework** | LangChain + `langchain-huggingface` | Native HF integration |
| **Testing** | pytest + Hypothesis | Python standard + property-based |
| **Storage** | Pinecone + JSON files | Cloud persistence for vectors |

### Why These Choices?

1. **Hugging Face Inference API**:
   - Free tier includes rate-limited access to many models
   - Pro tier ($9/mo) provides higher rate limits
   - No per-token costs like OpenAI
   - Access to open models (Mixtral, Llama, Falcon, etc.)
   - Easy to switch models without code changes

2. **Mixtral-8x7B-Instruct**:
   - Best open-source model for instruction-following
   - 32k context window (sufficient for RAG + conversation history)
   - Excellent at maintaining character/persona
   - Available on HF Inference API free tier

3. **Pinecone Free Tier**:
   - 1 index, 100k vectors free
   - Fully managed, no infrastructure
   - More than sufficient for MVP (50-100 docs)
   - Easy upgrade path to paid tiers

4. **sentence-transformers for Embeddings**:
   - Free via HF Inference API
   - `all-MiniLM-L6-v2` is fast and high-quality
   - 384-dimensional vectors (efficient storage)

### Alternative Model Options

| Model | Strengths | Best For |
|-------|-----------|----------|
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | Best overall quality | Primary generation |
| `mistralai/Mistral-7B-Instruct-v0.2` | Faster, lighter | Development/testing |
| `meta-llama/Llama-2-70b-chat-hf` | Strong reasoning | Complex debates |
| `HuggingFaceH4/zephyr-7b-beta` | Good instruction-following | Budget option |

### Cost Comparison

| Provider | MVP Monthly Cost (Est.) |
|----------|------------------------|
| **HF Inference API (Free)** | $0 (rate-limited) |
| **HF Inference API (Pro)** | $9/month |
| **OpenAI GPT-4o-mini** | $50-100/month |
| **OpenAI GPT-4-turbo** | $200-500/month |

---

## MVP Component Design

### 1. Delegate Agent Module

```python
# src/agents/delegate_agent.py

from dataclasses import dataclass
from typing import Literal
from langchain_huggingface import HuggingFaceEndpoint

@dataclass
class DelegateProfile:
    name: str
    state: str
    role: str
    ideology: Literal["federalist", "anti-federalist", "moderate"]
    speaking_frequency: Literal["rare", "occasional", "frequent"]
    personality_traits: list[str]
    known_positions: dict[str, str]  # topic -> stance
    rhetorical_style: str
    few_shot_examples: list[str]

class DelegateAgent:
    def __init__(self, profile: DelegateProfile, llm: HuggingFaceEndpoint, rag: RAGSystem):
        self.profile = profile
        self.llm = llm
        self.rag = rag
        self.conversation_history: list[Message] = []

    async def generate_response(self, topic: str, context: ConversationContext) -> DialogueTurn:
        # 1. Retrieve relevant sources
        sources = await self.rag.retrieve(topic, self.profile.name)

        # 2. Build prompt with profile, context, and sources
        prompt = self._build_prompt(topic, context, sources)

        # 3. Generate response via HF Inference API
        response = await self.llm.ainvoke(prompt)

        # 4. Format with citations
        return self._format_turn(response, sources)

    def _build_prompt(self, topic: str, context: ConversationContext, sources: list[Source]) -> str:
        """Build instruction prompt for Mixtral."""
        return f"""<s>[INST] You are {self.profile.name}, a delegate from {self.profile.state} at the 1787 Constitutional Convention.

PERSONALITY: {self.profile.rhetorical_style}
IDEOLOGY: {self.profile.ideology}
KNOWN POSITIONS: {self.profile.known_positions}

HISTORICAL SOURCES:
{self._format_sources(sources)}

RECENT DEBATE:
{self._format_history(context.recent_history)}

Current topic: {topic}
Current date: {context.current_date}

Respond as {self.profile.name} would, using 18th-century language and rhetoric.
Include citations to sources using【source】format.
Never reference events after September 17, 1787.
[/INST]"""
```

### 2. RAG System Module

```python
# src/knowledge/rag_system.py

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

class RAGSystem:
    def __init__(self, index_name: str = "farrand-sources"):
        # Initialize HF embeddings (free via Inference API)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize Pinecone
        pc = Pinecone()  # Uses PINECONE_API_KEY env var
        self.vectorstore = PineconeVectorStore(
            index=pc.Index(index_name),
            embedding=self.embeddings
        )

        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"date_max": {"$lte": "1787-09-17"}}
            }
        )

    async def retrieve(self, query: str, delegate_name: str = None) -> list[Source]:
        """Retrieve relevant historical sources for a query."""
        # Add delegate-specific context to query
        enhanced_query = f"{delegate_name}: {query}" if delegate_name else query

        docs = await self.retriever.ainvoke(enhanced_query)
        return [self._doc_to_source(doc) for doc in docs]

    def _doc_to_source(self, doc: Document) -> Source:
        return Source(
            text=doc.page_content,
            citation=f"【{doc.metadata['collection']}, {doc.metadata['doc_id']}】",
            date=doc.metadata['date'],
            author=doc.metadata.get('author')
        )

    @classmethod
    def ingest_documents(cls, documents: list[dict], index_name: str = "farrand-sources"):
        """Ingest documents into Pinecone."""
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        texts = [doc["content"] for doc in documents]
        metadatas = [
            {
                "collection": doc["collection"],
                "doc_id": doc["id"],
                "date": doc["date"],
                "author": doc.get("author", "unknown")
            }
            for doc in documents
        ]

        PineconeVectorStore.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            index_name=index_name
        )
```

### 3. LLM Configuration Module

```python
# src/config/llm_config.py

import os
from langchain_huggingface import HuggingFaceEndpoint

def get_llm(
    model_id: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature: float = 0.4,
    max_new_tokens: int = 512
) -> HuggingFaceEndpoint:
    """
    Initialize Hugging Face Inference API client.

    Requires HUGGINGFACEHUB_API_TOKEN environment variable.
    """
    return HuggingFaceEndpoint(
        repo_id=model_id,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
        task="text-generation",
    )

# Environment variables required:
# - HUGGINGFACEHUB_API_TOKEN: Your HF API token (free at huggingface.co)
# - PINECONE_API_KEY: Your Pinecone API key (free tier available)
```

### 4. Conversation Manager

```python
# src/orchestration/conversation_manager.py

from datetime import date

class ConversationManager:
    def __init__(self, agents: dict[str, DelegateAgent], validator: ConstraintValidator):
        self.agents = agents
        self.validator = validator
        self.history: list[DialogueTurn] = []
        self.current_topic: str = None
        self.current_date: date = date(1787, 5, 25)

    async def run_turn(self) -> DialogueTurn:
        # 1. Select next speaker
        speaker = self._select_speaker()

        # 2. Build context
        context = ConversationContext(
            topic=self.current_topic,
            recent_history=self.history[-10:],
            current_date=self.current_date
        )

        # 3. Generate response via HF Inference API
        turn = await self.agents[speaker].generate_response(self.current_topic, context)

        # 4. Validate
        validation = self.validator.validate(turn)
        if not validation.is_valid:
            turn = await self._regenerate_with_feedback(speaker, validation.feedback)

        # 5. Record and return
        self.history.append(turn)
        return turn

    def _select_speaker(self) -> str:
        """Simple speaker selection for MVP."""
        # Prioritize: relevance to topic > hasn't spoken recently > random
        # Respect speaking frequency constraints
        ...
```

### 5. Constraint Validator

```python
# src/validation/constraint_validator.py

from datetime import date
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    feedback: str | None

class ConstraintValidator:
    def __init__(self, anachronism_terms: set[str]):
        self.anachronism_terms = anachronism_terms
        self.date_boundary = date(1787, 9, 17)

    def validate(self, turn: DialogueTurn) -> ValidationResult:
        errors = []

        # Check for anachronistic terms
        for term in self.anachronism_terms:
            if term.lower() in turn.text.lower():
                errors.append(f"Anachronistic term detected: '{term}'")

        # Check date references
        date_refs = self._extract_dates(turn.text)
        for ref in date_refs:
            if ref > self.date_boundary:
                errors.append(f"Future date reference: {ref}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            feedback=self._generate_feedback(errors) if errors else None
        )
```

---

## MVP Data Requirements

### 1. Delegate Profiles (7 files)

```
data/delegates/
├── madison.json
├── hamilton.json
├── mason.json
├── sherman.json
├── morris.json
├── franklin.json
└── washington.json
```

Each profile contains:
- Biographical summary
- Ideological stance with supporting evidence
- Known positions on key issues
- Speaking style characteristics
- 3-5 few-shot dialogue examples from primary sources

### 2. Knowledge Base Documents (50-100 docs)

```
data/sources/
├── farrand/           # 30-40 key excerpts from Farrand's Records
├── founders_online/   # 15-20 letters/papers
└── contemporary/      # 5-10 period documents
```

Priority documents:
- Madison's Notes (primary source for debates)
- Virginia Plan text
- New Jersey Plan text
- Key speeches by MVP delegates
- Contemporary letters showing delegate positions

### 3. Anachronism Dictionary

```
data/anachronisms.txt
```

Start with 50-100 terms covering:
- Post-1787 political concepts (e.g., "democracy" in modern sense)
- Technology terms (railroad, telegraph, etc.)
- Modern idioms and expressions
- Post-ratification constitutional concepts

### 4. Episode Test Fixtures (3-5)

```
tests/fixtures/episodes/
├── virginia_plan_introduction.json
├── new_jersey_plan_response.json
└── great_compromise_debate.json
```

---

## MVP Development Phases

### Phase 1: Foundation (Core Infrastructure)
- [ ] Project structure and interfaces
- [ ] Pinecone index setup and document ingestion pipeline
- [ ] Hugging Face Inference API integration
- [ ] Basic prompt templates for Mixtral instruction format
- [ ] Environment configuration (HF token, Pinecone API key)

### Phase 2: Single Agent Demo
- [ ] Madison agent with full profile
- [ ] RAG retrieval integration with Pinecone
- [ ] Basic dialogue generation via HF API
- [ ] Citation formatting

### Phase 3: Multi-Agent Conversation
- [ ] All 7 delegate agents with profiles
- [ ] Conversation manager with turn-taking
- [ ] Speaker selection logic
- [ ] Conversation history tracking

### Phase 4: Validation & Quality
- [ ] Anachronism filter
- [ ] Basic constraint validation
- [ ] Turn rejection and regeneration
- [ ] Output formatting (structured format)

### Phase 5: Testing & Polish
- [ ] 3-5 episode test fixtures
- [ ] Property tests for core invariants
- [ ] CLI interface
- [ ] Basic documentation

---

## Key MVP Simplifications

### 1. Memory System
**MVP**: Store last 10 turns per agent in memory (no persistence)
**Later**: Vector-based semantic memory with recency weighting

### 2. Speaker Selection
**MVP**: Round-robin with basic topic relevance scoring
**Later**: Sophisticated selection based on ideology, speaking frequency, handoff signals

### 3. Validation
**MVP**: Keyword-based anachronism filter
**Later**: Secondary LLM validation, stylometric analysis

### 4. Citation Validation
**MVP**: Verify citation format, basic source existence check
**Later**: Line number validation, exact text matching

### 5. Testing
**MVP**: 5-10 core property tests, 3-5 episode fixtures
**Later**: Full 51 properties, 15-20 episodes, regression suite

---

## MVP Success Criteria

1. **Functional Demo**: 10+ turn conversation among 7 delegates on a single topic
2. **Historical Grounding**: ≥70% of turns include citations to primary sources
3. **Consistency**: Delegates maintain consistent ideological positions
4. **No Anachronisms**: Zero modern terms in generated dialogue
5. **Distinct Voices**: Human evaluator can distinguish delegate speaking styles
6. **Episode Validation**: Pass 3 core historical episode tests

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| HF API rate limits | Use Pro tier ($9/mo) or implement request queuing |
| Model quality variance | Test multiple models (Mixtral, Mistral, Zephyr), pick best |
| RAG quality issues | Start with curated, high-quality sources |
| Inconsistent delegate behavior | Extensive few-shot examples, low temperature (0.3-0.4) |
| Scope creep | Strict MVP boundary enforcement |
| Historical inaccuracy | Expert review of initial episode fixtures |
| Pinecone index limits | Free tier has 100k vectors - sufficient for MVP |

### HF Inference API Considerations

1. **Rate Limits**: Free tier is rate-limited. For development, use smaller model (Mistral-7B) to iterate faster.

2. **Model Availability**: Some models may be temporarily unavailable. Have fallback models configured.

3. **Latency**: HF Inference API can have variable latency. Implement timeouts and retries.

```python
# Example retry configuration
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_with_retry(llm, prompt):
    return await llm.ainvoke(prompt)
```

---

## Post-MVP Roadmap

### V1.1: Enhanced Agents
- Expand to 15 delegates
- Add memory persistence
- Improve speaker selection

### V1.2: Full Validation
- Secondary LLM validation
- Stylometric analysis
- Comprehensive episode tests

### V1.3: Scale & Polish
- All 55 delegates
- Full Convention timeline
- Performance optimization
- Production deployment

---

## Appendix A: Dependencies

### Core Dependencies (requirements.txt)

```
# LLM & Embeddings
langchain>=0.1.0
langchain-huggingface>=0.0.3
huggingface-hub>=0.20.0

# Vector Database
pinecone-client>=3.0.0
langchain-pinecone>=0.0.3

# Utilities
python-dotenv>=1.0.0
tenacity>=8.2.0
pydantic>=2.0.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.23.0
hypothesis>=6.0.0
```

### Environment Variables (.env)

```bash
# Hugging Face (free at huggingface.co/settings/tokens)
HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Pinecone (free at pinecone.io)
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## Appendix B: Project Structure

```
project-farrand/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── delegate_agent.py
│   │   └── profiles.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── llm_config.py
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── rag_system.py
│   │   └── document_loader.py
│   ├── orchestration/
│   │   ├── __init__.py
│   │   └── conversation_manager.py
│   ├── validation/
│   │   ├── __init__.py
│   │   └── constraint_validator.py
│   └── main.py
├── data/
│   ├── delegates/
│   ├── sources/
│   └── anachronisms.txt
├── tests/
│   ├── unit/
│   ├── property/
│   └── fixtures/
│       └── episodes/
├── docs/
│   └── mvp-architecture-recommendations.md
├── .env.example
├── pyproject.toml
└── README.md
```

---

## Conclusion

This MVP architecture focuses on demonstrating the core value proposition—historically-grounded, multi-agent dialogue—while avoiding the complexity of the full system. By limiting to 7 delegates, 3 debate topics, and simplified validation, the MVP can be built and validated quickly while establishing patterns that scale to the full implementation.

The key insight is that **historical authenticity** is the differentiator, not scale. An MVP with 7 well-modeled delegates producing authentic dialogue is more valuable than 55 poorly-modeled agents producing generic output.
