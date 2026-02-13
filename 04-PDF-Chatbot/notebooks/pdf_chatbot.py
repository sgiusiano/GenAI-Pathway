#!/usr/bin/env python3
"""
Simple CLI Chatbot for PDF Q&A using ChromaDB and OpenAI
"""

import requests
import fitz  # PyMuPDF
from io import BytesIO
import os
from typing import List
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import chromadb
from chromadb.utils import embedding_functions
import openai


class PDFChatbot:
    def __init__(self):
        """Initialize the chatbot with OpenAI and ChromaDB"""
        load_dotenv()
        openai.api_key = os.environ["OPENAI_API_KEY"]
        
        # Create OpenAI embedding function
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            openai.api_key,
            model_name="text-embedding-3-small"
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0, model='gpt-4')
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template("""
        You are a helpful assistant that answers questions based on the provided context.
        Use only the information from the context to answer the question.
        If the answer is not in the context, say "I don't have enough information to answer this question."

        Context:
        {context}
                
        Question: {question}
                
        Answer:
        """)
        
        self.collection = None
    
    def read_pdf_from_url(self, url: str) -> str:
        """Read PDF from URL and extract text"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            pdf_bytes = BytesIO(response.content)
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()
            
            pdf_document.close()
            return text
            
        except Exception as e:
            print(f"Error reading PDF from URL: {e}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into chunks"""
        if not text:
            return []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        return text_splitter.split_text(text)
    
    def create_or_get_vector_db(self, chunks: List[str], collection_name: str, 
                              persist_directory: str = "./chroma_db") -> chromadb.Collection:
        """Create or load a ChromaDB collection"""
        client = chromadb.PersistentClient(path=persist_directory)
        
        try:
            collection = client.get_collection(name=collection_name, embedding_function=self.openai_ef)
            print(f"Collection found! It has {collection.count()} documents")
            return collection
        except Exception:
            print("Collection not found; creating it...")
            collection = client.create_collection(
                name=collection_name,
                embedding_function=self.openai_ef,
                metadata={"description": "PDF document embeddings with OpenAI"}
            )
            
            if chunks:
                print(f"Embedding {len(chunks)} chunks...")
                documents = chunks
                ids = [f"chunk_{i}" for i in range(len(chunks))]
                metadatas = [{"chunk_index": i, "chunk_length": len(chunk)} for i, chunk in enumerate(chunks)]
                
                collection.add(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas
                )
                
                print(f"Successfully embedded {len(chunks)} chunks into ChromaDB")
            
            return collection
    
    def retrieve_context(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieve relevant context from ChromaDB collection"""
        if not self.collection:
            return []
        
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return results['documents'][0]
    
    def load_pdf(self, url: str, collection_name: str):
        """Load and process a PDF from URL"""
        print(f"Loading PDF from: {url}")
        text = self.read_pdf_from_url(url)
        
        if not text:
            print("Failed to load PDF")
            return False
        
        print("Splitting text into chunks...")
        chunks = self.chunk_text(text)
        
        print("Creating vector database...")
        self.collection = self.create_or_get_vector_db(chunks, collection_name)
        
        print(f"✅ PDF loaded successfully! Ready to answer questions.")
        return True
    
    def ask(self, question: str) -> str:
        """Ask a question and get an answer"""
        if not self.collection:
            return "No PDF loaded. Please load a PDF first."
        
        # Retrieve context
        context_docs = self.retrieve_context(question)
        
        if not context_docs:
            return "No relevant context found."
        
        # Create and run chain
        chain = (
            RunnableLambda(lambda x: {
                "context": "\n\n".join(context_docs),
                "question": question
            })
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain.invoke({"question": question})


def main():
    """Main CLI interface"""
    chatbot = PDFChatbot()
    
    print("🤖 PDF Chatbot - Ask questions about any PDF!")
    print("=" * 50)
    
    # Default to requests library documentation
    default_url = "https://app.readthedocs.org/projects/requests/downloads/pdf/latest/"
    
    print(f"\nLoading default PDF (Requests library documentation)...")
    if not chatbot.load_pdf(default_url, "requests_docs"):
        print("Failed to load default PDF. Exiting.")
        return
    
    print("\n💡 Commands:")
    print("  - Type your question and press Enter")
    print("  - Type 'load <url>' to load a different PDF")
    print("  - Type 'quit' or 'exit' to quit")
    print("\n" + "=" * 50)
    
    while True:
        try:
            user_input = input("\n🔍 Ask a question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower().startswith('load '):
                url = user_input[5:].strip()
                collection_name = url.split('/')[-1].replace('.pdf', '').replace('.', '_')
                print(f"\nLoading new PDF: {url}")
                chatbot.load_pdf(url, collection_name)
                continue
            
            print("\n🤔 Thinking...")
            answer = chatbot.ask(user_input)
            print(f"\n💬 Answer: {answer}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
