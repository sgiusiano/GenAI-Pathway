# scripts/pdf_downloader.py

import requests
import PyPDF2
from io import BytesIO
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PDFProcessor:
    """Simple PDF downloader and text extractor"""
    
    def __init__(self):
        self.session = requests.Session()
        self.chunk_size = 2000
        self.overlap = 200
        
    def _download_pdf(self, url):
        """Download PDF from URL"""
        print(f"📥 Downloading PDF from {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            print(f"❌ Error downloading PDF: {e}")
            return None
    
    def _extract_text(self, pdf_content):
        """Extract text from PDF content"""
        print("📖 Extracting text from PDF...")
        
        try:
            pdf_file = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            page_count = len(pdf_reader.pages)
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                
                if i % 10 == 0:  # Progress every 10 pages
                    print(f"   📄 Processed {i+1}/{page_count} pages")
            
            print(f"✅ Extracted {len(text)} characters from {page_count} pages")
            return text
            
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return None
    
    def get_text_from_url(self, url):
        """Download PDF and extract text in one step"""
        pdf_content = self._download_pdf(url)
        if pdf_content:
            return self._extract_text(pdf_content)
        return None

    def _clean_text(self, text):
        """Clean and normalize text"""
        print("🧹 Cleaning text...")
        
        # Check if text is None or empty
        if not text or not isinstance(text, str):
            print("❌ Error: No text to clean or text is not a string")
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^THE SECOND WORLD WAR\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^POLICIES\s*$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def chunk_text(self, text):
        """Main chunking method using RecursiveCharacterTextSplitter"""
        print("🔍 Starting recursive character text splitting...")
        
        # Check if text is valid
        if not text or not isinstance(text, str):
            print("❌ Error: No text provided for chunking")
            return []
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Initialize RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Split the text
        chunks = text_splitter.split_text(cleaned_text)
        
        # Format chunks with metadata
        all_chunks = []
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'id': i,
                'text': chunk,
                'section_header': None,
                'section_chunk_index': 0,
                'char_count': len(chunk)
            })
        
        print(f"✅ Total chunks created: {len(all_chunks)} (avg {sum(len(c['text']) for c in all_chunks)//len(all_chunks) if all_chunks else 0} chars each)")
        return all_chunks
