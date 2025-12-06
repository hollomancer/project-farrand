import os
from enum import Enum
from langchain_huggingface import HuggingFaceEndpoint

class ModelTier(Enum):
    """Model tiers for different use cases."""
    DEVELOPMENT = "meta-llama/Llama-3.1-8B-Instruct"      # Fast iteration
    PRODUCTION = "meta-llama/Llama-3.1-70B-Instruct"      # Best quality
    BUDGET = "mistralai/Mixtral-8x7B-Instruct-v0.1"       # Cost-conscious

def get_llm(
    model_id: str = ModelTier.PRODUCTION.value,
    temperature: float = 0.4,
    max_new_tokens: int = 512
) -> HuggingFaceEndpoint:
    """
    Initialize Hugging Face Inference API client.

    Args:
        model_id: HF model repo ID (default: Llama-3.1-70B-Instruct)
        temperature: Sampling temperature (0.3-0.5 recommended for consistency)
        max_new_tokens: Max response length

    Requires HUGGINGFACEHUB_API_TOKEN environment variable.
    HF Pro subscription ($9/mo) recommended for 70B model access.
    """
    return HuggingFaceEndpoint(
        repo_id=model_id,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
        task="text-generation",
    )

# Quick helpers for common configurations
def get_dev_llm() -> HuggingFaceEndpoint:
    """Fast 8B model for development and testing."""
    return get_llm(model_id=ModelTier.DEVELOPMENT.value)

def get_prod_llm() -> HuggingFaceEndpoint:
    """High-quality 70B model for production."""
    return get_llm(model_id=ModelTier.PRODUCTION.value)
