# Technology Stack

## Language & Runtime
- **Python 3.11+** - Primary implementation language

## LLM Infrastructure
- **Model**: Llama 3.1 70B Instruct (via Hugging Face Inference API)
  - Development: Llama 3.1 8B Instruct (faster iteration)
  - Alternative: Mixtral 8x7B Instruct
- **Embeddings**: BAAI/bge-large-en-v1.5 (1024-dim, state-of-the-art retrieval)
- **Framework**: LangChain with langchain-huggingface integration
- **Temperature**: 0.3-0.5 (low for consistency and formal language)

## Vector Database
- **Pinecone** - Managed vector search for RAG system
- Stores document embeddings with metadata (author, date, type, line numbers)
- Filters enforce historical date boundary (≤ September 17, 1787)

## Testing
- **pytest** - Unit and integration tests
- **Hypothesis** - Property-based testing for correctness properties
- **pytest-asyncio** - Async test support

## Environment Variables
```bash
HUGGINGFACEHUB_API_TOKEN  # HF API token (Pro tier recommended)
PINECONE_API_KEY          # Pinecone API key
```

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Development
```bash
# Run tests
pytest

# Run property tests
pytest tests/property/

# Run episode tests
pytest tests/fixtures/episodes/

# Run with coverage
pytest --cov=src
```

### Simulation
```bash
# Run single episode
python src/main.py --episode virginia_plan_introduction

# Run full session
python src/main.py --date 1787-05-30 --topic representation
```

## Architecture Patterns

### Multi-Agent System
- Independent delegate agents with distinct LLM prompts
- Central conversation manager for orchestration
- Turn-taking controller for speaker selection

### RAG Pipeline
1. Query construction from agent context
2. Vector search in Pinecone (top-k retrieval)
3. Source excerpts injected into agent prompt
4. Generated dialogue includes citations

### Memory System
- Per-agent vector-based memory store
- Recency weighting for retrieval
- Cross-session persistence

### Validation
- Anachronism keyword filter
- Historical constraint validator
- Secondary LLM evaluation for quality
- Episode test framework for regression testing
