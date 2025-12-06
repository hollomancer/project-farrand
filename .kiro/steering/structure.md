# Project Structure

```
project-farrand/
├── src/
│   ├── agents/              # Delegate agent implementations
│   │   ├── delegate_agent.py    # Core agent class
│   │   └── profiles.py          # Agent profile definitions
│   ├── config/              # Configuration and LLM setup
│   │   └── llm_config.py        # HF Inference API configuration
│   ├── knowledge/           # RAG and knowledge base
│   │   ├── rag_system.py        # RAG retrieval engine
│   │   └── document_loader.py   # Document ingestion
│   ├── orchestration/       # Conversation management
│   │   └── conversation_manager.py  # Turn-taking and state
│   ├── validation/          # Historical constraints
│   │   └── constraint_validator.py  # Anachronism filter
│   └── main.py              # Simulation entry point
├── data/
│   ├── delegates/           # Delegate profile JSONs (7 files)
│   ├── sources/             # Historical documents
│   │   ├── farrand/             # Farrand's Records excerpts
│   │   ├── founders_online/     # Founders Online documents
│   │   └── contemporary/        # Period documents
│   └── anachronisms.txt     # Forbidden modern terms
├── tests/
│   ├── unit/                # Unit tests
│   ├── property/            # Property-based tests (51 properties)
│   └── fixtures/
│       └── episodes/        # Historical episode test fixtures
├── docs/
│   ├── vision.md            # Full system specification
│   └── mvp-architecture-recommendations.md  # MVP design
├── .kiro/
│   ├── specs/               # Spec-driven development
│   │   └── constitutional-convention-sim/
│   │       ├── requirements.md  # 20 requirements
│   │       ├── design.md        # Architecture and interfaces
│   │       └── tasks.md         # 31-phase implementation plan
│   └── steering/            # AI assistant guidance (this folder)
├── .env                     # Environment variables (not in git)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
└── README.md
```

## Key Organizational Principles

### Modular Architecture
Each subsystem (agents, knowledge, orchestration, memory) is independent with clear interfaces defined in `design.md`.

### Spec-Driven Development
The `.kiro/specs/` folder contains the complete specification:
- **requirements.md**: 20 functional requirements with acceptance criteria
- **design.md**: Component interfaces, data models, 51 correctness properties
- **tasks.md**: 31-phase implementation plan with property tests

### Test-First Approach
Every requirement has corresponding property tests. The implementation plan includes 51 property tests that validate correctness properties.

### Historical Data Separation
All historical content lives in `data/`:
- Delegate profiles are JSON files with biographical data, positions, and style
- Source documents organized by collection
- Anachronism dictionary for validation

### Episode Testing
`tests/fixtures/episodes/` contains historical episode test fixtures that validate agent behavior against documented Convention events (Virginia Plan debates, Great Compromise, etc.).

## File Naming Conventions

- **Delegate profiles**: `{lastname}.json` (e.g., `madison.json`)
- **Episode fixtures**: `{event_name}.json` (e.g., `virginia_plan_introduction.json`)
- **Test files**: `test_{module}.py` for unit tests, `property_{module}.py` for property tests
- **Source documents**: Organized by collection, preserve original naming where possible
