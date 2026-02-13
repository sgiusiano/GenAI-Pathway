import json
import chromadb
from chromadb.config import Settings

def build_vectordb(input_file, db_path):
    """Build ChromaDB vector database from enriched videos"""

    with open(input_file, 'r') as f:
        videos = json.load(f)

    print(f"Building vector database with {len(videos)} videos...")

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=db_path)

    # Create or get collections
    try:
        client.delete_collection("f1_videos_text")
        client.delete_collection("f1_videos_image")
    except:
        pass

    text_collection = client.create_collection(
        name="f1_videos_text",
        metadata={"description": "F1 video text embeddings"}
    )

    image_collection = client.create_collection(
        name="f1_videos_image",
        metadata={"description": "F1 video image embeddings"}
    )

    # Prepare data
    text_embeddings = []
    image_embeddings = []
    text_ids = []
    image_ids = []
    text_metadatas = []
    image_metadatas = []
    text_documents = []
    image_documents = []

    for video in videos:
        video_id = video['video_id']

        # Metadata
        metadata = {
            "video_id": video_id,
            "title": video['title'],
            "url": video['url'],
            "duration_tag": video.get('duration_tag', 'medium'),
            "duration_seconds": video['duration_seconds'],
            "video_type": video.get('video_type', 'knowledge'),
            "category": video.get('category', 'Racing'),
            "subcategory": video.get('subcategory', 'general'),
            "popularity_score": video.get('popularity_score', 0),
            "engagement_like_score": video.get('engagement_like_score', 0),
            "engagement_comment_score": video.get('engagement_comment_score', 0),
            "relevance_score": video.get('relevance_score', 0),
            "published_at": video['published_at'],
            "view_count": video['view_count']
        }

        # Text collection
        if video.get('text_embedding'):
            text_embeddings.append(video['text_embedding'])
            text_ids.append(f"text_{video_id}")
            text_metadatas.append(metadata)
            text_documents.append(f"{video['title']}. {video.get('cleaned_description', '')}")

        # Image collection
        if video.get('image_embedding'):
            image_embeddings.append(video['image_embedding'])
            image_ids.append(f"image_{video_id}")
            image_metadatas.append(metadata)
            image_documents.append(f"Thumbnail for: {video['title']}")

    # Add to collections
    if text_embeddings:
        text_collection.add(
            embeddings=text_embeddings,
            documents=text_documents,
            metadatas=text_metadatas,
            ids=text_ids
        )
        print(f"  Added {len(text_embeddings)} text embeddings")

    if image_embeddings:
        image_collection.add(
            embeddings=image_embeddings,
            documents=image_documents,
            metadatas=image_metadatas,
            ids=image_ids
        )
        print(f"  Added {len(image_embeddings)} image embeddings")

    print(f"✅ Vector database built at: {db_path}")

if __name__ == "__main__":
    input_file = "/Users/santiagoarielgiusiano/Documents/Personal/GenAI Pathway/genF1/enriched_videos.json"
    db_path = "/Users/santiagoarielgiusiano/Documents/Personal/GenAI Pathway/genF1/chroma_db"

    build_vectordb(input_file, db_path)
