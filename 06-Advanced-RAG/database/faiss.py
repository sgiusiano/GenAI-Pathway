from langchain_community.vectorstores import FAISS


class faissHandler:
    def __init__(self):
        self.vector_store = None

    def create_faiss_index(self, documents, embeddings):
        """Create a FAISS vector store from documents and their embeddings"""
        self.vector_store = FAISS.from_embeddings(
            text_embeddings=[(doc.page_content, emb) for doc, emb in zip(documents, embeddings)],
            embedding=None, # Embedding is None because we already have embeddings
            metadatas=[doc.metadata for doc in documents]
        )
        return self.vector_store
