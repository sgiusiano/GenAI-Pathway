from retriever import F1VideoRetriever

def recommend_videos(query, top_k=5, category_filter=None, duration_filter=None):
    """
    Simple recommendation interface

    Args:
        query: User question/query
        top_k: Number of videos to recommend
        category_filter: Optional category (e.g., "Technical", "Teams")
        duration_filter: Optional duration tag ("short", "medium", "long")

    Returns:
        List of recommended videos with metadata
    """

    db_path = "/Users/santiagoarielgiusiano/Documents/Personal/GenAI Pathway/genF1/chroma_db"
    retriever = F1VideoRetriever(db_path)

    # Build filters
    filters = {}
    if category_filter:
        filters['category'] = category_filter
    if duration_filter:
        filters['duration_tag'] = duration_filter

    # Retrieve
    results = retriever.retrieve(
        query=query,
        top_k=top_k,
        filters=filters if filters else None,
        text_weight=0.7
    )

    # Format results
    recommendations = []
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        recommendations.append({
            'rank': i,
            'title': meta['title'],
            'url': meta['url'],
            'duration': f"{meta['duration_seconds']//60}:{meta['duration_seconds']%60:02d}",
            'duration_tag': meta['duration_tag'],
            'type': meta['video_type'],
            'category': f"{meta['category']} > {meta['subcategory']}",
            'views': f"{meta['view_count']:,}",
            'popularity_score': meta.get('popularity_score', 0),
            'engagement_like_score': meta.get('engagement_like_score', 0),
            'engagement_comment_score': meta.get('engagement_comment_score', 0),
            'relevance_score': meta.get('relevance_score', 0),
            'match_score': result['score'],
            'text_similarity': result.get('text_similarity', 0),
            'keyword_boost': result.get('keyword_boost', 0),
            'published': meta['published_at'][:10]
        })

    return recommendations

def print_recommendations(recommendations):
    """Pretty print recommendations"""
    print("\n" + "="*80)
    print("F1 VIDEO RECOMMENDATIONS")
    print("="*80)

    for rec in recommendations:
        print(f"\n#{rec['rank']} | {rec['title']}")
        print(f"   URL: {rec['url']}")
        print(f"   Duration: {rec['duration']} ({rec['duration_tag']}) | Type: {rec['type']}")
        print(f"   Category: {rec['category']}")
        print(f"   Views: {rec['views']} | Published: {rec['published']}")
        print(f"   Match: {rec['match_score']:.3f} (text: {rec['text_similarity']:.3f}, kw: {rec['keyword_boost']:.3f})")
        print(f"   Scores → Pop: {rec['popularity_score']:.3f} | Like: {rec['engagement_like_score']:.3f} | Comment: {rec['engagement_comment_score']:.3f} | Total: {rec['relevance_score']:.3f}")

    print("\n" + "="*80 + "\n")

# Example usage
if __name__ == "__main__":
    # Example 1: General query
    query = "How does F1 suspension work?"
    print(f"Query: {query}")
    results = recommend_videos(query, top_k=5)
    print_recommendations(results)

    # # Example 2: With category filter
    # query = "McLaren innovations"
    # print(f"\nQuery: {query}")
    # results = recommend_videos(query, top_k=3, category_filter="McLaren")
    # print_recommendations(results)

    # # Example 3: Short videos only
    # query = "F1 braking system"
    # print(f"\nQuery: {query} (Short videos)")
    # results = recommend_videos(query, top_k=3, duration_filter="short")
    # print_recommendations(results)
