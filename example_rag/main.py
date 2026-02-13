import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Add this BEFORE any imports
from rag.models.langchain_model import LangchainRAG
from rag.settings import credentials

def initialize(config):
    """Initialize the RAG system by loading documents and creating vector store."""
    print("Initializing RAG system...")
    rag = LangchainRAG(
        embedding_model=config["embedding_model"],
        llm_model=config["llm_model"],
        vector_store=config["vector_store"],
        search_type=config['search_type'],
        use_semantic_chunking=False,  # Enable semantic chunking by default
    )

    documents = rag.load_and_process_documents(
        config["data_path"],
        file_type=config["file_type"]
    )

    
    #if rag.vector_store:
    #    rag.load_existing_vector_store()
    #else:
    #    rag.create_vector_store(documents)
    rag.create_vector_store(documents)
    
    rag.setup_qa_chain()
    print("RAG system ready for queries.")
    return rag

def main():
    """Main function to run the RAG system."""
    print("Welcome to the RAG system!")
    question = input("\nEnter your question about request library: ").strip()
    # Configuration model last challenge
    print("Starting RAG system previous challenge...")
    config = {
        "data_path": "./data/",
        "embedding_model": "huggingface",
        "llm_model": "openai",
        "vector_store": "chroma",
        "search_type": "similarity",
        "file_type": "pdf"
    }

    rag_system = initialize(config)
    print("Running RAG system...")
    result = rag_system.query(question)
    print("\nAnswer:", result['answer'])
    print("Source documents:")
    for doc in result['source_documents']:
        print(doc.metadata)
    print("RAG system terminated.\n\n\n\n")

    #Configuration model current challenge
    print("Starting RAG system current challenge...")
    config = {
        "data_path": "./data/",
        "embedding_model": "huggingface",
        "llm_model": "openai",
        "vector_store": "chroma",
        "search_type": "mmr",
        "file_type": "pdf"
    }

    rag_system = initialize(config)
    print("Running RAG system...")
    result = rag_system.query(question)
    print("\nAnswer:", result['answer'])
    print("Source documents:")
    for doc in result['source_documents']:
        print(doc.metadata)
    print("RAG system terminated.\n\n\n\n")

if __name__ == "__main__":
    main()
