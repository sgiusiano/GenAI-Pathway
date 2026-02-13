import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_description_with_llm(title, description):
    """Use GPT-4 to extract only relevant technical/contextual content"""

    prompt = f"""Extract ONLY the relevant technical and contextual content from this F1 video description.

Title: {title}
Description: {description}

REMOVE: Promotional links, discount codes, social media handles, CTAs, ads, job listings
KEEP: Technical explanations, story/narrative, historical context, names, factual F1 information

Return ONLY the cleaned text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract relevant technical content from F1 descriptions. Return only cleaned text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error: {e}")
        return description[:500]
