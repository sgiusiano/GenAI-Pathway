from rag.utils.model_utils import get_embeddings, get_llm
from rag.utils.document_utils import DocumentProcessor
from rag.utils.vector_store_utils import VectorStoreManager
from rag.utils.chain_utils import QAChainBuilder
from rag.settings.constants import RETRIEVER_K

class LangchainRAG:
    def __init__(self, 
                 embedding_model="huggingface",
                 use_semantic_chunking=False,
                 llm_model="openAI",
                 vector_store="chroma",
                 k=RETRIEVER_K,
                 search_type="similarity",
                 score_threshold=0.7,
                 fetch_k=20):
        """
        Initialize RAG system with configurable components
        """
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.vector_store_type = vector_store
        self.vector_store = None
        self.qa_chain = None
        self.use_semantic_chunking = use_semantic_chunking

        
        # Initialize embeddings
        self.embeddings = get_embeddings(embedding_model)
        # Initialize LLM
        self.llm = get_llm(llm_model)

        self.document_processor = DocumentProcessor()
        self.vector_store_manager = VectorStoreManager(
            self.vector_store_type,
            self.embeddings
        )

        self.qa_chain_builder = QAChainBuilder(k=k,
                                               search_type=search_type,
                                               score_threshold=score_threshold,
                                               fetch_k=fetch_k)

    def load_and_process_documents(self, data_path, file_type="txt"):
        documents = self.document_processor.load_documents(data_path, file_type)
        return self.document_processor.split_documents(documents,
                                                       use_semantic=self.use_semantic_chunking,
                                                       embeddings=self.embeddings)

    def create_vector_store(self, texts):
        self.vector_store_manager.create_vector_store(texts)
        self.vector_store = self.vector_store_manager.vector_store

    def load_existing_vector_store(self):
        self.vector_store_manager.load_existing_vector_store()
        self.vector_store = self.vector_store_manager.vector_store

    def setup_qa_chain(self):
        self.qa_chain = self.qa_chain_builder.build_qa_chain(self.llm, self.vector_store)
        return self.qa_chain

    def query(self, question):
        if not self.qa_chain:
            raise ValueError("QA chain not initialized. Call setup_qa_chain() first.")

        result = self.qa_chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "source_documents": result.get("source_documents", [])
        }
