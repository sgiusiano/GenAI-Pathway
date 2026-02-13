# F1 Multimodal RAG System

Multimodal RAG system for F1 video recommendations using CLIP embeddings and ChromaDB.

## Setup

1. Install dependencies:
```bash
pip install torch transformers chromadb pillow requests openai python-dotenv numpy
```

2. Set up `.env` with your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
```

## Pipeline

Run scripts in order:

### 1. Enrich Metadata
Adds LLM-generated metadata and calculates engagement scores:
```bash
cd scripts
python 1_enrich_metadata.py
```

Adds:
- `duration_tag` (short/medium/long)
- `cleaned_tags` (removes common F1 words)
- `video_type` (news/knowledge/gossip)
- `category` + `subcategory`
- Scores: `popularity_score`, `engagement_like_score`, `engagement_comment_score`, `relevance_score`

### 2. Clean Descriptions
Uses GPT-4o-mini to remove promotional content:
```bash
python 2_clean_descriptions.py
```

Import and use:
```python
from scripts.clean_descriptions import clean_description_with_llm
cleaned = clean_description_with_llm(title, description)
```

### 3. Create Embeddings
Generate CLIP embeddings for text and images:
```bash
python 3_create_embeddings.py
```

Creates:
- `text_embedding` from title + cleaned description
- `image_embedding` from `thumbnail_maxres`
- `enriched_videos_images.json` with base64 image store

### 4. Build Vector Database
Index embeddings in ChromaDB:
```bash
python 4_build_vectordb.py
```

Creates `chroma_db/` with two collections:
- `f1_videos_text`: Text embeddings
- `f1_videos_image`: Image embeddings

## Usage

### Simple Recommendations

```python
from rag.recommend import recommend_videos, print_recommendations

# Basic query
results = recommend_videos("How does F1 suspension work?", top_k=5)
print_recommendations(results)

# With filters
results = recommend_videos(
    query="McLaren innovations",
    top_k=3,
    category_filter="Teams",
    duration_filter="short"
)
```

### Advanced Retrieval

```python
from rag.retriever import F1VideoRetriever

retriever = F1VideoRetriever("genF1/chroma_db")

results = retriever.retrieve(
    query="F1 aerodynamics explained",
    top_k=5,
    filters={"category": "Technical"},
    use_mmr=True,  # Maximum Marginal Relevance re-ranking
    text_weight=0.7  # Balance text vs image similarity
)
```

## Features

✅ **Multimodal**: CLIP embeddings for text + images
✅ **Smart Metadata**: LLM-generated categorization (9 new fields)
✅ **Clean Content**: Ad-free descriptions
✅ **Hybrid Search**: Semantic similarity + metadata filtering
✅ **MRR Re-ranking**: Balances relevance with diversity
✅ **Engagement Scores**: Popularity + like rate + comment rate

## Structure

```
genF1/
├── f1data/
│   └── driver61_videos.json          # Original data
├── scripts/
│   ├── 1_enrich_metadata.py          # GPT-4 categorization
│   ├── 2_clean_descriptions.py       # LLM text cleaning
│   ├── 3_create_embeddings.py        # CLIP embeddings
│   └── 4_build_vectordb.py           # ChromaDB indexing
├── rag/
│   ├── retriever.py                   # Hybrid retrieval + MRR
│   └── recommend.py                   # Simple query interface
├── enriched_videos.json               # Output with all metadata
├── enriched_videos_images.json        # Base64 image store
└── chroma_db/                         # Vector database
```

## Metadata Fields

Each video includes:

**Original**: `video_id`, `title`, `description`, `url`, `duration_seconds`, `view_count`, `like_count`, `comment_count`, `tags`, `thumbnail_maxres`, `published_at`

**Enriched**:
- `duration_tag`: short/medium/long (quartile-based)
- `cleaned_tags`: Removes "F1", "Formula 1", etc.
- `video_type`: news | knowledge | gossip
- `category`: Teams | Technical | Drivers | Racing | Engineering
- `subcategory`: Specific subtopic
- `popularity_score`: Normalized view count
- `engagement_like_score`: Normalized like rate
- `engagement_comment_score`: Normalized comment count
- `relevance_score`: 0.5×popularity + 0.2×likes + 0.3×comments
- `cleaned_description`: Ad-free content
- `text_embedding`: 512-dim CLIP vector
- `image_embedding`: 512-dim CLIP vector

## Filters

Available metadata filters:

```python
filters = {
    "category": "Technical",         # Teams | Technical | Drivers | Racing | Engineering
    "subcategory": "suspension",     # Specific subtopic
    "video_type": "knowledge",       # news | knowledge | gossip
    "duration_tag": "medium"         # short | medium | long
}
```
