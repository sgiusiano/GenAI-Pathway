import json
import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def calculate_scores(videos):
    """Calculate normalized popularity and engagement scores"""
    # Extract metrics
    view_counts = [v['view_count'] for v in videos]
    like_rates = [(v['like_count'] / v['view_count']) if v['view_count'] > 0 else 0 for v in videos]
    comment_counts = [v['comment_count'] for v in videos]

    # Get max values for normalization
    max_views = max(view_counts) if view_counts else 1
    max_like_rate = max(like_rates) if like_rates else 1
    max_comments = max(comment_counts) if comment_counts else 1

    for i, video in enumerate(videos):
        video['popularity_score'] = view_counts[i] / max_views
        video['engagement_like_score'] = like_rates[i] / max_like_rate if max_like_rate > 0 else 0
        video['engagement_comment_score'] = comment_counts[i] / max_comments

        # Overall relevance score
        video['relevance_score'] = (
            video['popularity_score'] * 0.5 +
            video['engagement_like_score'] * 0.2 +
            video['engagement_comment_score'] * 0.3
        )

    return videos

def create_duration_tags(videos):
    """Create duration tags based on quartiles"""
    durations = [v['duration_seconds'] for v in videos]
    q1 = np.percentile(durations, 25)
    q3 = np.percentile(durations, 75)

    for video in videos:
        duration = video['duration_seconds']
        if duration <= q1:
            video['duration_tag'] = 'short'
        elif duration <= q3:
            video['duration_tag'] = 'medium'
        else:
            video['duration_tag'] = 'long'

    return videos

def clean_tags(videos):
    """Remove common F1-related words from tags"""
    stop_words = {'f1', 'formula 1', 'formula', 'motorsport', 'driver61'}

    for video in videos:
        if video.get('tags'):
            cleaned = [tag for tag in video['tags']
                      if tag.lower() not in stop_words]
            video['cleaned_tags'] = cleaned
        else:
            video['cleaned_tags'] = []

    return videos

def classify_video_with_gpt4(title, description):
    """Use GPT-4 to classify video type and category"""

    # Remove promotional content for better classification
    desc_lines = description.split('\n')
    relevant_desc = []
    for line in desc_lines:
        lower_line = line.lower()
        # Skip lines with promotional content
        if any(skip in lower_line for skip in ['head over to', 'use the code', 'join our',
                                                 'on sale now', 'instagram', 'facebook',
                                                 'twitter', 'tiktok', '@', 'http']):
            continue
        relevant_desc.append(line)

    # Get last meaningful paragraph (usually the actual video description)
    clean_desc = '\n'.join(relevant_desc)
    if len(clean_desc) > 500:
        clean_desc = clean_desc[:500] + "..."

    prompt = f"""Analyze this F1 video and classify it:

Title: {title}
Description: {clean_desc}

Provide classification in JSON format:
{{
  "video_type": "news|knowledge|gossip",
  "category": "Teams|Technical|Drivers|Racing|Engineering",
  "subcategory": "specific subcategory based on these examples:
    - Teams: ferrari, mercedes, mclaren, redbull
    - Technical: engine, aero, suspension, gearbox, brakes, steering
    - Drivers: verstappen, hamilton, leclerc, norris, alonso
    - Racing: race, qualifying, overtake, crash
    - Engineering: design, factory, manufacturing"
}}

Rules:
- video_type: "news" = current facts/events, "knowledge" = explaining concepts, "gossip" = polemic/opinion
- Choose the MOST relevant category and subcategory
- Be concise"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert F1 content classifier. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"Error classifying video: {e}")
        return {
            "video_type": "knowledge",
            "category": "Racing",
            "subcategory": "general"
        }

def enrich_metadata(input_file, output_file):
    """Main function to enrich video metadata"""

    print("Loading videos...")
    with open(input_file, 'r') as f:
        videos = json.load(f)

    print(f"Processing {len(videos)} videos...")

    # Step 1: Calculate scores
    print("1. Calculating scores...")
    videos = calculate_scores(videos)

    # Step 2: Create duration tags
    print("2. Creating duration tags...")
    videos = create_duration_tags(videos)

    # Step 3: Clean tags
    print("3. Cleaning tags...")
    videos = clean_tags(videos)

    # Step 4: Classify with GPT-4
    print("4. Classifying videos with GPT-4...")
    for i, video in enumerate(videos):
        print(f"   Processing {i+1}/{len(videos)}: {video['title'][:50]}...")

        classification = classify_video_with_gpt4(video['title'], video['description'])
        video['video_type'] = classification.get('video_type', 'knowledge')
        video['category'] = classification.get('category', 'Racing')
        video['subcategory'] = classification.get('subcategory', 'general')

    # Save enriched data
    print(f"\nSaving enriched metadata to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(videos, f, indent=2)

    print("✅ Metadata enrichment complete!")
    print(f"\nNew fields added:")
    print("  - popularity_score")
    print("  - engagement_like_score")
    print("  - engagement_comment_score")
    print("  - relevance_score")
    print("  - duration_tag")
    print("  - cleaned_tags")
    print("  - video_type")
    print("  - category")
    print("  - subcategory")

if __name__ == "__main__":
    input_file = "/Users/santiagoarielgiusiano/Documents/Personal/GenAI Pathway/genF1/f1data/driver61_videos.json"
    output_file = "/Users/santiagoarielgiusiano/Documents/Personal/GenAI Pathway/genF1/enriched_videos.json"

    enrich_metadata(input_file, output_file)
