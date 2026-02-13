import torch
import os
import base64
import io
import requests
import fitz  # PyMuPDF
import numpy as np
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import CLIPProcessor, CLIPModel
from PIL import Image


load_dotenv()

## set up the environment
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

class PDFMultimodalProcessor:
    """PDF processor that extracts both text and images, and generates embeddings using CLIP."""
    
    def __init__(self):
        self.chunk_size = 2000
        self.overlap = 200
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.overlap)
        self.embedding_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.embedding_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.vector_store = None
    
    def get_emdedding_model(self):
        return self.embedding_model
        
    def _download_pdf(self, url):
        """Download PDF from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            print(f"❌ Error downloading PDF: {e}")
            return None
    
    def embed_image(self, image_data):
        """Embed image using CLIP"""
        if isinstance(image_data, str):  # If path
            image = Image.open(image_data).convert("RGB")
        else:  # If PIL Image
            image = image_data
        
        inputs = self.embedding_processor(
            images=image, 
            return_tensors="pt"
        )
        with torch.no_grad():
            features = self.embedding_model.get_image_features(**inputs)
            # Normalize embeddings to unit vector
            features = features / features.norm(dim=-1, keepdim=True)
            return features.squeeze().detach().cpu().numpy()
    
    def embed_text(self, text):
        """Embed text using CLIP."""
        inputs = self.embedding_processor(
            text=text, 
            return_tensors="pt", 
            padding=True,
            truncation=True,
            max_length=77  # CLIP's max token length
        )
        with torch.no_grad():
            features = self.embedding_model.get_text_features(**inputs)
            # Normalize embeddings
            features = features / features.norm(dim=-1, keepdim=True)
            return features.squeeze().detach().cpu().numpy()
        
    def _extract_text_and_images(self, pdf_content):
        """Extract text and images from PDF content"""

        try:
            pdf_file = fitz.open(stream=pdf_content, filetype="pdf")

        except Exception as e:
            print(f" Error extracting text/images: {e}")
            return None, []
        
        all_docs = []
        all_embeddings = []
        image_data_store = {}  # Store actual image data for LLM

        for i,page in enumerate(pdf_file):
            ## process text
            text=page.get_text()
            if text.strip():
                ##create temporary document for splitting
                temp_doc = Document(page_content=text, metadata={"page": i, "type": "text"})
                text_chunks = self.text_splitter.split_documents([temp_doc])

                #Embed each chunk using CLIP
                for chunk in text_chunks:
                    embedding = self.embed_text(chunk.page_content)
                    all_embeddings.append(embedding)
                    all_docs.append(chunk)

            for img_index, img in enumerate(page.get_images(full=True)):
                try:
                    xref = img[0]
                    base_image = pdf_file.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convert to PIL Image
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    
                    # Create unique identifier
                    image_id = f"page_{i}_img_{img_index}"
                    
                    # Store image as base64 for later use with GPT-4V
                    buffered = io.BytesIO()
                    pil_image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    image_data_store[image_id] = img_base64
                    
                    # Embed image using CLIP
                    embedding = self.embed_image(pil_image)
                    all_embeddings.append(embedding)
                    
                    # Create document for image
                    image_doc = Document(
                        page_content=f"[Image: {image_id}]",
                        metadata={"page": i, "type": "image", "image_id": image_id}
                    )
                    all_docs.append(image_doc)
                    
                except Exception as e:
                    print(f"Error processing image {img_index} on page {i}: {e}")
                    continue

        pdf_file.close()

        return all_docs, all_embeddings, image_data_store
    
    def process_pdf(self, url):
        """Download PDF, extract text and images, chunk text, and create vector store"""
        pdf_content = self._download_pdf(url)
        if not pdf_content:
            return None, None, None
        
        all_docs, all_embeddings, image_data_store = self._extract_text_and_images(pdf_content)
        
        if not all_docs:
            print("❌ No content extracted from PDF.")
            return None, None, None
        
        embeddings_array = np.array(all_embeddings) # Convert list to numpy array
        return all_docs, embeddings_array, image_data_store
