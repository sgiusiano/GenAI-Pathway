from langchain_community.vectorstores import Chroma
from rag.settings.models_config import VECTOR_STORES


class VectorStoreManager:
    def __init__(self, vector_store_type, embeddings):
        self.vector_store_type = vector_store_type
        self.embeddings = embeddings
        self.vector_store = None
        self.persist_directory = None

    def _set_directory_by_store(self) :
        persist_directory = VECTOR_STORES.get(self.vector_store_type, {}).get("persist_dir", self.persist_directory)
        if not persist_directory:
            raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")
        self.persist_directory = persist_directory

    def create_vector_store(self, documents):
        # First get persist directory from settings
        self._set_directory_by_store()
        if self.vector_store_type == "chroma":
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )

    def load_existing_vector_store(self):
        # First get persist directory from settings
        self._set_directory_by_store()
        try:
            if self.vector_store_type == "chroma":
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            return self.vector_store
        except Exception as e:
            raise Exception(f"Could not load existing vector store: {e}")
