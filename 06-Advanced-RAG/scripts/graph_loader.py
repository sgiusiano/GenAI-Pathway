import json
from database.neo4j import Neo4jHandler

class graphQLoader:
    def __init__(self, client: Neo4jHandler):
        self.client = client

    def load_entities_to_neo4j(self):
        """Load processed entities and relations into Neo4j database"""
        
        # Load processed data
        with open('data/processed/entities.json', 'r') as f:
            entities = json.load(f)
        
        with open('data/processed/relations.json', 'r') as f:
            relations = json.load(f)
        
        print(f"Loading {len(entities)} entities and {len(relations)} relations to Neo4j...")
        
        # Clear existing data
        self.client.execute_query("MATCH (n) DETACH DELETE n")
        
        # Create entities
        for entity in entities:
            entity_type = entity['type'].replace(" ", "_")
            name = entity['name'].replace("'", "\\'")
            context = entity.get('context', '').replace("'", "\\'")
            chunk_id = entity.get('chunk_id', 0)
            source_context = entity.get('source_context', '').replace("'", "\\'")
            
            query = f"""
            CREATE (e:{entity_type} {{
                name: '{name}',
                context: '{context}',
                chunk_id: {chunk_id},
                source_context: '{source_context}'
            }})
            """
            self.client.execute_query(query)
        
        # Create relationships
        for relation in relations:
            source = relation['source'].replace("'", "\\'")
            target = relation['target'].replace("'", "\\'")
            rel_type = relation['relation'].replace(" ", "_").replace("-", "_")
            confidence = relation.get('confidence', 1.0)
            chunk_id = relation.get('chunk_id', 0)
            source_context = relation.get('source_context', '').replace("'", "\\'")
            
            query = f"""
            MATCH (s) WHERE s.name = '{source}'
            MATCH (t) WHERE t.name = '{target}'
            CREATE (s)-[r:{rel_type} {{
                confidence: {confidence},
                chunk_id: {chunk_id},
                source_context: '{source_context}'
            }}]->(t)
            """
            self.client.execute_query(query)
        
        print("✅ Data loaded successfully!")
