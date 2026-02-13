import torch
import chromadb
import re
from transformers import CLIPProcessor, CLIPModel

class F1VideoRetriever:
    """Hybrid retriever with semantic similarity search + keyword boosting"""

    def __init__(self, db_path):
        self.client = chromadb.PersistentClient(path=db_path)
        self.text_collection = self.client.get_collection("f1_videos_text")
        self.image_collection = self.client.get_collection("f1_videos_image")

        # CLIP for query embeddings
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def embed_query(self, query):
        """Embed query text using CLIP"""
        inputs = self.processor(
            text=query,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=77
        )
        with torch.no_grad():
            features = self.model.get_text_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
            return features.squeeze().detach().cpu().numpy()

    def extract_keywords(self, query):
        """Extract important keywords from query"""
        # Remove stop words and extract meaningful terms
        stop_words = {'how', 'does', 'what', 'is', 'the', 'a', 'an', 'work', 'works', 'do'}
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords

    def calculate_keyword_score(self, keywords, title, category, subcategory):
        """Calculate keyword match score"""
        score = 0
        title_lower = title.lower()
        category_lower = f"{category} {subcategory}".lower()

        for keyword in keywords:
            # Exact match in title (high weight)
            if keyword in title_lower:
                score += 0.3
            # Match in category/subcategory
            if keyword in category_lower:
                score += 0.2

        return min(score, 1.0)  # Cap at 1.0

    def retrieve(self, query, top_k=5, filters=None, text_weight=0.7):
        """
        Hybrid retrieval: text + image embeddings with optional filters

        Args:
            query: User query string
            top_k: Number of results to return
            filters: Dict of metadata filters (e.g., {"category": "Technical"})
            text_weight: Weight for text vs image (0-1, higher = more text)
        """
        query_embedding = self.embed_query(query)

        # Search both collections
        text_results = self.text_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filters
        )

        image_results = self.image_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filters
        )

        # Combine results with weights
        combined = {}

        # Text results
        for i, video_id in enumerate(text_results['ids'][0]):
            vid = video_id.replace('text_', '')
            distance = text_results['distances'][0][i]
            # Better similarity: lower distance = higher similarity
            similarity = 1 - min(distance / 2, 1)

            combined[vid] = {
                'metadata': text_results['metadatas'][0][i],
                'text_similarity': similarity,
                'image_similarity': 0
            }

        # Image results
        for i, video_id in enumerate(image_results['ids'][0]):
            vid = video_id.replace('image_', '')
            distance = image_results['distances'][0][i]
            similarity = 1 - min(distance / 2, 1)

            if vid in combined:
                combined[vid]['image_similarity'] = similarity
            else:
                combined[vid] = {
                    'metadata': image_results['metadatas'][0][i],
                    'text_similarity': 0,
                    'image_similarity': similarity
                }

        # Extract keywords from query
        keywords = self.extract_keywords(query)

        # Calculate combined scores
        scored_results = []
        for vid, data in combined.items():
            semantic_score = (
                text_weight * data['text_similarity'] +
                (1 - text_weight) * data['image_similarity']
            )

            # Keyword matching boost (additive, not multiplicative)
            keyword_boost = 0
            title_lower = data['metadata'].get('title', '').lower()
            subcategory_lower = data['metadata'].get('subcategory', '').lower()

            for keyword in keywords:
                if keyword in title_lower:
                    keyword_boost += 0.15  # Strong boost for title match
                elif keyword in subcategory_lower:
                    keyword_boost += 0.08  # Medium boost for category match

            # Small boost by relevance_score
            relevance_boost = data['metadata'].get('relevance_score', 0) * 0.05

            # Final score: semantic + keyword boost + small relevance
            final_score = semantic_score + keyword_boost + relevance_boost

            scored_results.append({
                'video_id': vid,
                'metadata': data['metadata'],
                'score': final_score,
                'text_similarity': data['text_similarity'],
                'image_similarity': data['image_similarity'],
                'semantic_score': semantic_score,
                'keyword_boost': keyword_boost
            })

        # Sort by score DESCENDING and return top_k highest scores
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:top_k]
