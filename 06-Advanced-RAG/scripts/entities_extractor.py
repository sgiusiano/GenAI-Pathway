# scripts/entity_extractor.py

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import json
import os
from pathlib import Path
from typing import List, Dict

class EntityExtractor:
    """Extract entities and relations using LLM and persist results"""
    
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=self.api_key
        )
        
        self.prompt = PromptTemplate(
            input_variables=["chunk_data"],
            template="""
            Extract WWII historical entities and relations from this text chunk.

            Text: {chunk_data}

            Return ONLY valid JSON:
            {{
                "entities": [
                    {{"type": "Person", "name": "Winston Churchill", "context": "British Prime Minister"}},
                    {{"type": "Organization", "name": "Wehrmacht", "context": "German Army"}},
                    {{"type": "Location", "name": "Belgrade", "context": "Yugoslav capital"}},
                    {{"type": "Event", "name": "Operation Barbarossa", "context": "German invasion of USSR"}}
                ],
                "relations": [
                    {{"source": "Winston Churchill", "relation": "LED", "target": "Britain", "confidence": 0.9}},
                    {{"source": "Wehrmacht", "relation": "INVADED", "target": "Yugoslavia", "confidence": 0.95}}
                ]
            }}

            Entity types: Person, Organization, Location, Event
            Relation types: LED, COMMANDED, INVADED, ALLIED_WITH, OPPOSED, PARTICIPATED_IN, OCCURRED_IN

            Keep names exact as they appear in text.
            """
        )
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def extract_from_chunk(self, chunk_data):
        """Extract entities and relations from a single chunk"""
        
        try:
            content = self.chain.invoke({"chunk_data": chunk_data['text']})
            
            # Clean up response if it has extra text
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content)
            
            # Add chunk metadata
            for entity in result.get("entities", []):
                entity["chunk_id"] = chunk_data["id"]
                entity["source_section"] = chunk_data.get("section_header")
                entity["source_context"] = chunk_data['text']
            
            for relation in result.get("relations", []):
                relation["chunk_id"] = chunk_data["id"]
                relation["source_section"] = chunk_data.get("section_header")
                relation["source_context"] = chunk_data['text']
            
            return result
        except Exception as e:
            print(f"Error processing chunk {chunk_data.get('id', 'unknown')}: {e}")
            return {"entities": [], "relations": []}
    
    def deduplicate_entities(self, entities):
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity['type'], entity['name'].lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        print(f"🔄 Deduplicated: {len(entities)} → {len(unique_entities)} entities")
        return unique_entities
    
    def save_results(self, chunks, entities, relations, output_dir="data/processed"):
        """Save all results to files"""
        print("💾 Saving results...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save chunks
        chunks_file = output_path / "semantic_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"   📄 Chunks saved: {chunks_file}")
        
        # Deduplicate and save entities
        unique_entities = self.deduplicate_entities(entities)
        entities_file = output_path / "entities.json"
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(unique_entities, f, indent=2, ensure_ascii=False)
        print(f"   👥 Entities saved: {entities_file}")
        
        # Save relations
        relations_file = output_path / "relations.json"
        with open(relations_file, 'w', encoding='utf-8') as f:
            json.dump(relations, f, indent=2, ensure_ascii=False)
        print(f"   🔗 Relations saved: {relations_file}")
