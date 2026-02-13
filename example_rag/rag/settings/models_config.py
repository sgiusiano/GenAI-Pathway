from rag.settings.constants import (
    CHROMA_DIRECTORY,
    LLM_TEMPERATURE,
    OPENAI_MODEL,
    HUGGING_EMBEDDING_MODEL
)


EMBEDDING_MODELS = {
    "openai": {
        "class": "OpenAIEmbeddings",
        "params": {
            "model": "text-embedding-3-small"
        }
    },
    "huggingface": {
        "class": "HuggingFaceEmbeddings",
        "params": {
            "model_name": HUGGING_EMBEDDING_MODEL
        }
    }
}


# LLM configurations
LLM_MODELS = {
    "openai": {
        "class": "ChatOpenAI",
        "params": {
            "temperature": LLM_TEMPERATURE,
            "model": OPENAI_MODEL
        }
    }
}

# Vector store configurations
VECTOR_STORES = {
    "chroma": {
        "persist_dir": CHROMA_DIRECTORY,
    }
}
