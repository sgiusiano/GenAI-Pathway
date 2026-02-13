"""Run the complete F1 RAG pipeline"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from scripts.enrich_metadata import enrich_metadata
from scripts.clean_descriptions import clean_description_with_llm
from scripts.create_embeddings import create_embeddings
from scripts.build_vectordb import build_vectordb

print("="*80)
print("F1 MULTIMODAL RAG PIPELINE")
print("="*80)

# Step 1: Enrich metadata
print("\n[1/4] Enriching metadata with GPT-4...")
enrich_metadata("f1data/driver61_videos.json", "enriched_videos.json")

# Step 2: Clean descriptions
print("\n[2/4] Cleaning descriptions with LLM...")
with open("enriched_videos.json", 'r') as f:
    videos = json.load(f)

for i, video in enumerate(videos, 1):
    video['cleaned_description'] = clean_description_with_llm(
        video['title'],
        video.get('description', '')
    )
    if i % 5 == 0:
        print(f"  {i}/{len(videos)} processed")

with open("enriched_videos.json", 'w') as f:
    json.dump(videos, f, indent=2)

# Step 3: Create embeddings
print("\n[3/4] Creating CLIP embeddings...")
create_embeddings("enriched_videos.json", "enriched_videos.json")

# Step 4: Build vector DB
print("\n[4/4] Building ChromaDB...")
build_vectordb("enriched_videos.json", "chroma_db")

print("\n" + "="*80)
print("✅ PIPELINE COMPLETE!")
print("="*80)
print("\nYou can now use:")
print("  python -c \"from rag.recommend import *; print_recommendations(recommend_videos('How does F1 suspension work?'))\"")
print("\nOr in a Python script:")
print("  from rag.recommend import recommend_videos, print_recommendations")
print("  results = recommend_videos('your query here', top_k=5)")
print("  print_recommendations(results)")
