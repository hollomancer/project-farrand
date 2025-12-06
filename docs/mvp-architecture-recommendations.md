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
│                       │  (ChromaDB)  │                          │
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
| **LLM Provider** | OpenAI GPT-4o-mini | Cost-effective, good quality for MVP |
| **Embeddings** | OpenAI text-embedding-3-small | Simple integration, adequate quality |
| **Vector DB** | ChromaDB (local) | Zero infrastructure, easy setup |
| **Framework** | LangChain | Battle-tested, good abstractions |
| **Testing** | pytest + Hypothesis | Python standard + property-based |
| **Storage** | SQLite + JSON files | Simple persistence, no server needed |

### Why These Choices?

1. **ChromaDB over Pinecone/Weaviate**: For MVP, local vector storage eliminates infrastructure complexity. Can migrate to managed solution later.

2. **GPT-4o-mini over GPT-4-turbo**: 10-15x cheaper, sufficient quality for MVP validation. Reserve GPT-4-turbo for production or secondary validation.

3. **LangChain over raw API**: Provides useful abstractions (chains, retrievers, memory) without over-engineering. Skip LangGraph complexity for MVP.

4. **SQLite over PostgreSQL**: No server management, portable, sufficient for MVP persistence needs.

---

## MVP Component Design

### 1. Delegate Agent Module

```python
# src/agents/delegate_agent.py

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
    def __init__(self, profile: DelegateProfile, llm: ChatOpenAI, rag: RAGSystem):
        self.profile = profile
        self.llm = llm
        self.rag = rag
        self.conversation_history: list[Message] = []

    async def generate_response(self, topic: str, context: ConversationContext) -> DialogueTurn:
        # 1. Retrieve relevant sources
        sources = await self.rag.retrieve(topic, self.profile.name)

        # 2. Build prompt with profile, context, and sources
        prompt = self._build_prompt(topic, context, sources)

        # 3. Generate response
        response = await self.llm.ainvoke(prompt)

        # 4. Format with citations
        return self._format_turn(response, sources)
```

### 2. RAG System Module

```python
# src/knowledge/rag_system.py

class RAGSystem:
    def __init__(self, vectorstore: Chroma, embeddings: OpenAIEmbeddings):
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.retriever = vectorstore.as_retriever(
            search_kwargs={"k": 5, "filter": {"date_max": "1787-09-17"}}
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
```

### 3. Conversation Manager

```python
# src/orchestration/conversation_manager.py

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

        # 3. Generate response
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

### 4. Constraint Validator

```python
# src/validation/constraint_validator.py

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
- [ ] ChromaDB setup with basic document ingestion
- [ ] OpenAI LLM integration
- [ ] Basic prompt templates

### Phase 2: Single Agent Demo
- [ ] Madison agent with full profile
- [ ] RAG retrieval integration
- [ ] Basic dialogue generation
- [ ] Citation formatting

### Phase 3: Multi-Agent Conversation
- [ ] All 7 delegate agents
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
| LLM costs during development | Use GPT-4o-mini, aggressive caching |
| RAG quality issues | Start with curated, high-quality sources |
| Inconsistent delegate behavior | Extensive few-shot examples, low temperature |
| Scope creep | Strict MVP boundary enforcement |
| Historical inaccuracy | Expert review of initial episode fixtures |

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

## Appendix: Project Structure

```
project-farrand/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── delegate_agent.py
│   │   └── profiles.py
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
├── pyproject.toml
└── README.md
```

---

## Conclusion

This MVP architecture focuses on demonstrating the core value proposition—historically-grounded, multi-agent dialogue—while avoiding the complexity of the full system. By limiting to 7 delegates, 3 debate topics, and simplified validation, the MVP can be built and validated quickly while establishing patterns that scale to the full implementation.

The key insight is that **historical authenticity** is the differentiator, not scale. An MVP with 7 well-modeled delegates producing authentic dialogue is more valuable than 55 poorly-modeled agents producing generic output.
