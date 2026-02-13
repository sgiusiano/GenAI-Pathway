#!/usr/bin/env python3
"""
Simple CLI Chatbot for PDF Q&A using ChromaDB and OpenAI
"""

import requests
import fitz  # PyMuPDF
from io import BytesIO
import os
import re
import logging
from typing import List, Dict
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker, LLMChainExtractor, EmbeddingsFilter, DocumentCompressorPipeline 
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_community.vectorstores.utils import filter_complex_metadata

import openai


class PDFChatbot:
    def __init__(self):
        """Initialize the chatbot with OpenAI and ChromaDB"""
        load_dotenv()
        openai.api_key = os.environ["OPENAI_API_KEY"]
        
        # Setup logging for LLM context tracking
        self._setup_logging()
        
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
        self.vector_store = None
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.cross_encoder_model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
    
    def _setup_logging(self):
        """Setup logging to track LLM context and interactions"""
        self.logger = logging.getLogger(f"pdf_chatbot.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
    def _log_llm_context(self, question: str, context: str, search_params: dict):
        """Log the context being passed to the LLM"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"LLM CONTEXT LOG - PDF CHATBOT")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Model: gpt-4")
        self.logger.info(f"Temperature: 0")
        self.logger.info(f"\nSearch Parameters:")
        for key, value in search_params.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info(f"\nUser Question:")
        self.logger.info(f"  {question}")
        self.logger.info(f"\nRetrieved Context ({len(context)} characters):")
        # Log first 500 characters of context to avoid overwhelming logs
        context_preview = context[:500] + "..." if len(context) > 500 else context
        self.logger.info(f"  {context_preview}")
        if len(context) > 500:
            self.logger.info(f"  [Context truncated - total length: {len(context)} characters]")
        self.logger.info(f"\nPrompt Template:")
        self.logger.info(f"  {self.prompt[:200]}...")
        self.logger.info(f"{'='*80}\n")
    
    def read_pdf_from_url(self, url: str) -> List[Dict]:
        """Read PDF from URL and extract text with page metadata"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            pdf_bytes = BytesIO(response.content)
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            pages_data = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                pages_data.append({
                    'text': page_text,
                    'page_number': page_num + 1,
                    'total_pages': pdf_document.page_count
                })
            
            pdf_document.close()
            return pages_data
            
        except Exception as e:
            print(f"Error reading PDF from URL: {e}")
            return None
    
    def extract_semantic_metadata(self, text: str) -> Dict:
        """Extract semantic metadata from text content"""
        metadata = {
            'topics': []
        }
        
        # Extract topic keywords relevant to requests library
        topic_keywords = [
            'authentication', 'session', 'cookie', 'header', 'ssl', 'certificate',
            'timeout', 'proxy', 'redirect', 'json', 'form', 'file', 'stream',
            'response', 'request', 'url', 'parameter', 'encoding', 'exception'
        ]
        
        for keyword in topic_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                metadata['topics'].append(keyword.lower())
        
        return metadata
    
    def extract_query_metadata(self, query: str) -> Dict:
        """Extract metadata filters from user query to guide retrieval"""
        filters = {}
        query_lower = query.lower()
        
        # Extract topic keywords
        topic_keywords = {
            'authentication': ['auth', 'login', 'credential', 'token', 'password', 'authentication'],
            'session': ['session', 'cookie', 'state'],
            'header': ['header', 'headers'],
            'ssl': ['ssl', 'tls', 'certificate', 'cert', 'https'],
            'timeout': ['timeout', 'time out', 'delay'],
            'proxy': ['proxy', 'proxies'],
            'redirect': ['redirect', 'redirection'],
            'json': ['json', 'javascript object notation'],
            'form': ['form', 'form-data', 'urlencoded'],
            'file': ['file', 'upload', 'download'],
            'stream': ['stream', 'streaming'],
            'response': ['response', 'reply'],
            'url': ['url', 'uri', 'endpoint'],
            'parameter': ['parameter', 'param', 'argument', 'arg'],
            'encoding': ['encoding', 'decode', 'encode', 'charset'],
            'exception': ['error', 'exception', 'fail', 'problem', 'issue']
        }
        
        mentioned_topics = []
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    mentioned_topics.append(topic)
                    break
        
        if mentioned_topics:
            # Use $in operator for ChromaDB list filtering
            filters['topics'] = {"$in": list(mentioned_topics)}
        
        return filters if filters else None
    
    def chunk_text(self, pages_data: List[Dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
        """Split text into chunks with semantic metadata"""
        if not pages_data:
            return []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks_with_metadata = []
        for page_data in pages_data:
            if not page_data['text'].strip():
                continue
                
            chunks = text_splitter.split_text(page_data['text'])
            for i, chunk in enumerate(chunks):
                # Extract semantic metadata from the chunk
                semantic_metadata = self.extract_semantic_metadata(chunk)
                
                # Combine with page metadata
                chunk_metadata = {
                    'page_number': page_data['page_number'],
                    'total_pages': page_data['total_pages'],
                    'chunk_index': i,
                    **semantic_metadata
                }
                doc={}
                # Create Document object
                doc['page_content']=chunk
                doc['metadata']=chunk_metadata
                chunks_with_metadata.append(doc)
        
        return chunks_with_metadata
    
    def init_vector_db(self, chunks_with_metadata: List[Dict], collection_name: str):
        """Create or load a ChromaDB collection with metadata"""
        CHROMA_PATH = './chroma_db'

        try:
            vectorstore = Chroma(
                persist_directory=CHROMA_PATH,
                collection_name=collection_name,
                embedding_function=self.embeddings
            )

            # Check if collection has documents
            existing_docs = vectorstore.get()
            if existing_docs['documents']:
                print(f"Collection found! It has {len(existing_docs['documents'])} documents")
                return vectorstore
            else:
                print("Collection exists but is empty, adding documents...")
                # Create Document objects for filter_complex_metadata
                documents = [
                    Document(page_content=doc['page_content'], metadata=doc['metadata'])
                    for doc in chunks_with_metadata
                ]
                filtered_docs = filter_complex_metadata(documents)
                texts = [doc.page_content for doc in filtered_docs]
                metadatas = [doc.metadata for doc in filtered_docs]
                vectorstore.add_texts(texts=texts, metadatas=metadatas)
                print(f"Successfully embedded {len(chunks_with_metadata)} chunks into existing collection")
                return vectorstore

        except Exception as e:
            print(f"Collection not found; creating it...{e}")
            # Create Document objects for filter_complex_metadata
            documents = [
                Document(page_content=doc['page_content'], metadata=doc['metadata'])
                for doc in chunks_with_metadata
            ]
            
            vectorstore = Chroma.from_documents(
                documents=filter_complex_metadata(documents),
                embedding=self.embeddings,
                persist_directory=CHROMA_PATH,
                collection_name=collection_name
            )

            print(f"Successfully embedded {len(chunks_with_metadata)} chunks into ChromaDB")
            return vectorstore
    
    def load_pdf(self, url: str, collection_name: str):
        """Load and process a PDF from URL"""
        print(f"Loading PDF from: {url}")
        pages_data = self.read_pdf_from_url(url)
        
        if not pages_data:
            print("Failed to load PDF")
            return False
        
        print("Splitting text into chunks with metadata extraction...")
        chunks_with_metadata = self.chunk_text(pages_data)
        
        print("Creating vector database with metadata...")
        # Create LangChain Chroma vector store for retriever functionality
        self.vector_store = self.init_vector_db(chunks_with_metadata, collection_name)
        
        print(f"✅ PDF loaded successfully! Ready to answer questions.")
        return True
    
    def retrieve_context(self, query: str, n_results: int = 3, search_type: str = "similarity", 
                        re_rank_compress: bool = False, use_metadata: bool = True) -> List[str]:
        """Retrieve relevant context from ChromaDB collection with optional metadata filtering"""
        if not self.vector_store:
            print("No vector store available. Please load a PDF first.")
            return []
        
        n_results = n_results * 4 if re_rank_compress else n_results # fetch more if re-ranking
        
        # Extract metadata from query
        metadata_filter = self.extract_query_metadata(query)
        
        # Prepare search kwargs with metadata filter
        base_search_kwargs = {"k": n_results}
        if metadata_filter:
            try:
                print(f"🔍 Auto-detected filters: {metadata_filter}")
                base_search_kwargs["filter"] = metadata_filter
                self.logger.info(f"Applying metadata filter: {metadata_filter}")
            except Exception as e:
                self.logger.error(f"Error applying metadata filter {metadata_filter}: {e}")
                # Continue without filter if there's an error
                self.logger.warning("Continuing search without metadata filter")
        
        # Configure retriever based on search_type
        if search_type == "mmr":
            search_kwargs = {"fetch_k": n_results * 2, "lambda_mult": 0.7}
            print(f"retriever kwargs: {search_kwargs}")
            retriever = self.vector_store.as_retriever(
                search_type="mmr",
                filter=base_search_kwargs['filter'] if use_metadata else None,
                search_kwargs=search_kwargs
            )
        elif search_type == "similarity_score_threshold":
            search_kwargs = {"score_threshold": 0.5}
            retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                filter=base_search_kwargs['filter'],
                search_kwargs=search_kwargs
            )
        else:  # default to similarity
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                filter=base_search_kwargs['filter']
            )
        
        # Retrieve documents
        if not re_rank_compress:
            # Get documents and return their content
            docs = retriever.invoke(query)
            return docs
        else:
            # Use CrossEncoderReranker for re-ranking
            re_ranker = CrossEncoderReranker(model=self.cross_encoder_model, top_n=n_results)
            # Add LLMChainExtractor to further compress context if needed
            llm = ChatOpenAI(model='gpt-4', temperature=0)
            prompt = ChatPromptTemplate.from_template("""
                Extract the key facts about {question} from the following text: {context}
                """
            )

            llm_chain = prompt | llm | StrOutputParser()
            # Create the compression pipeline
            extractor = LLMChainExtractor(llm_chain=llm_chain)
            emb_filter = EmbeddingsFilter(embeddings=self.embeddings, similarity_threshold=0.5)
            compress_pipe = DocumentCompressorPipeline(transformers=[re_ranker, emb_filter, extractor])
            compression_retriever = ContextualCompressionRetriever(
                base_retriever=retriever,
                base_compressor=compress_pipe
            )
            docs = compression_retriever.invoke(query)
            return docs
            
    
    def ask(self, question: str, search_type: str = "similarity", n_results: int = 3, 
           re_rank_compress: bool = True) -> str:
        """Ask a question and get an answer using the retrieve_context function with metadata filtering
        
        Args:
            question: The question to ask
            search_type: Type of search ("similarity", "mmr", "similarity_score_threshold")
            n_results: Number of results to return
            re_rank_compress: Whether to apply reranking and compression
        """
        if not self.vector_store:
            return "No PDF loaded. Please load a PDF first."
        
        # Get context using our retrieve_context function with metadata filtering
        context_docs = self.retrieve_context(
            question, 
            n_results=n_results, 
            search_type=search_type, 
            re_rank_compress=re_rank_compress
        )
        context_docs = [doc.page_content for doc in context_docs]
        context = "\n\n".join(context_docs)
        
        # Log the context being passed to LLM
        search_params = {
            "search_type": search_type,
            "n_results": n_results,
            "re_rank_compress": re_rank_compress,
            "context_chunks_retrieved": len(context_docs)
        }
        self._log_llm_context(question, context, search_params)
        
        # Create and run chain
        chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )

        response = chain.invoke({"context": context, "question": question})
        
        self.logger.info(f"LLM Response received - Length: {len(response)} characters")
        
        return response


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
