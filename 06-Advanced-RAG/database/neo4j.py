from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv
import os

load_dotenv()

class Neo4jHandler:
    def __init__(self):
        self.graph = Neo4jGraph(
            url='bolt://localhost:7687', 
            username=os.getenv('NEO4J_USERNAME'),
            password=os.getenv('NEO4J_PASSWORD')
        )


    def execute_query(self, query: str):
        return self.graph.query(query)
    
    def get_graph(self) -> Neo4jGraph:
        return self.graph
    