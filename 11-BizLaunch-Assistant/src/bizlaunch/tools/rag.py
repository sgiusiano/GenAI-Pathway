from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.tools import tool


class LegalRAG:
    def __init__(self, docs_path: str, persist_directory: str | None = None):
        self.docs_path = Path(docs_path)
        self.persist_directory = Path(persist_directory) if persist_directory else None
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize vector database from persisted store or create new one."""
        # Load existing persisted vector store if available
        if self.persist_directory and self.persist_directory.exists():
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            return

        # Create new vector store from documents
        docs = []
        pdf_files = list(self.docs_path.glob("*.pdf"))

        if not pdf_files:
            docs = self._create_mock_documents()
        else:
            for pdf_file in pdf_files:
                loader = PyPDFLoader(str(pdf_file))
                docs.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # Create and optionally persist vector store
        if self.persist_directory:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
        else:
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings
            )

    def query(self, question: str, k: int = 3) -> str:
        docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context


def create_rag_tool(rag: LegalRAG):
    @tool
    def query_regulations(question: str) -> str:
        """Consulta regulaciones legales, impuestos y requisitos para negocios en Córdoba.

        Args:
            question: Pregunta sobre aspectos legales, impuestos o habilitaciones
        """
        context = rag.query(question)
        return f"Información legal relevante:\n\n{context}"

    return query_regulations
