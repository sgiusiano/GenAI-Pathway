import os

from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from rag.settings.constants import (CHUNK_OVERLAP, CHUNK_SIZE)


class DocumentProcessor:
    def __init__(self, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_documents(self, data_path, file_type="txt"):
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data path {data_path} doesn't exist")

        documents = []

        if file_type == "txt":
            loader = self._get_loader(data_path, "*.txt", TextLoader)
        elif file_type == "pdf":
            loader = self._get_loader(data_path, "*.pdf", PyPDFLoader)
        else:
            raise ValueError("Supported file types: txt, pdf")

        documents = loader.load()
        return documents

    def _get_loader(self, data_path, glob_pattern, loader_cls):
        if os.path.isdir(data_path):
            return DirectoryLoader(data_path, glob=glob_pattern, loader_cls=loader_cls)
        return loader_cls(data_path)

    def _split_documents_simple(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

        chunks = text_splitter.split_documents(documents)

        return chunks

    def _split_documents_semantic(self, documents, embeddings):
        semantic_splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=90,
            buffer_size=1,                         # Context window around breaks
            sentence_split_regex='(?<=[.?!])\s+',  # Split on sentence endings
            add_start_index=True,
            min_chunk_size=100,                    # Prevent tiny chunks
            number_of_chunks=None                  # Algorithm will decide number of chunks
        )

        chunks = semantic_splitter.split_documents(documents)

        return chunks

    def split_documents(self, documents, use_semantic=False, embeddings=None):
        """
        Splits documents into manageable chunks.
        Uses semantic chunking if embeddings are provided, otherwise uses simple text splitting.
        """
        chunks = []
        if use_semantic:
            chunks = self._split_documents_semantic(documents, embeddings=embeddings)
        else:
            chunks = self._split_documents_simple(documents)

        return chunks
