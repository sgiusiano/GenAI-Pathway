import torch
import json
import requests
import base64
import io
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

class VideoEmbedder:
    """Create CLIP embeddings for video text and thumbnails"""

    def __init__(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def embed_text(self, text):
        """Embed text using CLIP"""
        inputs = self.processor(
            text=text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=77
        )
        with torch.no_grad():
            features = self.model.get_text_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
            return features.squeeze().detach().cpu().numpy()

    def embed_image(self, image_url):
        """Download and embed image using CLIP"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            image = Image.open(io.BytesIO(response.content)).convert("RGB")

            # Store as base64 for later GPT-4V use
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            # Create embedding
            inputs = self.processor(images=image, return_tensors="pt")
            with torch.no_grad():
                features = self.model.get_image_features(**inputs)
                features = features / features.norm(dim=-1, keepdim=True)
                embedding = features.squeeze().detach().cpu().numpy()

            return embedding, img_base64

        except Exception as e:
            print(f"Error embedding image: {e}")
            return None, None

def create_embeddings(input_file, output_file):
    """Create embeddings for all videos"""

    with open(input_file, 'r') as f:
        videos = json.load(f)

    print(f"Creating embeddings for {len(videos)} videos...")

    embedder = VideoEmbedder()
    image_store = {}

    for i, video in enumerate(videos, 1):
        # Text embedding from cleaned description
        text = f"{video['title']}. {video.get('cleaned_description', '')}"
        text_embedding = embedder.embed_text(text)
        video['text_embedding'] = text_embedding.tolist()

        # Image embedding from thumbnail
        img_embedding, img_base64 = embedder.embed_image(video['thumbnail_maxres'])

        if img_embedding is not None:
            video['image_embedding'] = img_embedding.tolist()
            image_store[video['video_id']] = img_base64
        else:
            video['image_embedding'] = None

        if i % 5 == 0:
            print(f"  {i}/{len(videos)} processed")

    # Save videos with embeddings
    with open(output_file, 'w') as f:
        json.dump(videos, f, indent=2)

    # Save image store separately
    image_store_file = output_file.replace('.json', '_images.json')
    with open(image_store_file, 'w') as f:
        json.dump(image_store, f, indent=2)

    print(f"✅ Embeddings created")
    print(f"   Videos: {output_file}")
    print(f"   Images: {image_store_file}")

if __name__ == "__main__":
    input_file = "/Users/santiagoarielgiusiano/Documents/Personal/GenAI Pathway/genF1/enriched_videos.json"
    output_file = "/Users/santiagoarielgiusiano/Documents/Personal/GenAI Pathway/genF1/enriched_videos.json"
    create_embeddings(input_file, output_file)
