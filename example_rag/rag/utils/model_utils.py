from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from rag.settings.models_config import EMBEDDING_MODELS, LLM_MODELS


def get_embeddings(model_name: str):
    model_config = EMBEDDING_MODELS.get(model_name)
    if not model_config:
        raise ValueError(f"Unsupported embedding model: {model_name}")
        
    if model_name == "openai":
        return OpenAIEmbeddings(**model_config["params"])
    else:
        return HuggingFaceEmbeddings(**model_config["params"])


def get_llm(model_name: str):
    model_config = LLM_MODELS.get(model_name)
    if not model_config:
        raise ValueError(f"Unsupported LLM model: {model_name}")
        
    if model_name == "openai":
        return ChatOpenAI(**model_config["params"])
