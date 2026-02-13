from langchain_openai import ChatOpenAI
from langchain_neo4j import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from typing import Any

from database.neo4j import Neo4jHandler


class RAGRetriever:
    """RAG retrieval using Neo4j graph database with GraphCypherQAChain"""
    
    def __init__(self, client: Neo4jHandler, llm: ChatOpenAI):
        self.client = client
        self.llm = llm
        
        # Create custom Cypher generation prompt with database context
        cypher_prompt = PromptTemplate.from_template("""
            You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query that returns comprehensive results.

            Database Context:
            This Neo4j database contains WWII historical information with the following structure:

            Node Types:
            - Person: Historical figures, leaders, soldiers, civilians
            - Organization: Armies, parties, resistance groups, governments  
            - Location: Countries, cities, regions, battlefields
            - Event: Battles, operations, meetings, historical incidents

            Relationship Types:
            - LED: Person led organization/country
            - COMMANDED: Person commanded military unit/operation
            - INVADED: Country/army invaded location
            - ALLIED_WITH: Entities formed alliances
            - OPPOSED: Entities fought against each other
            - PARTICIPATED_IN: Person/organization participated in event
            - OCCURRED_IN: Event happened in location

            Node Properties (ALWAYS return these):
            - name: Entity name (string) - REQUIRED
            - context: Descriptive context from source (string) - REQUIRED  
            - chunk_id: Source chunk identifier - REQUIRED

            QUERY STRATEGY:
            Always prioritize returning SOME context over returning nothing. Better to be broad and get related information than be specific and get empty results.

            QUERY SELECTION STRATEGY:
            1. For "Who led/commanded/headed X?" -> Use LEADERSHIP pattern
            2. For "What was X's role?" -> Use ENTITY ROLE pattern  
            3. For "Who opposed/fought X?" -> Use OPPOSITION pattern
            4. For general questions -> Use BROAD EXPLORATION pattern

            Query Patterns:

            LEADERSHIP PATTERN - For "who led/commanded" questions:
            MATCH (person:Person)-[r:LED|COMMANDED]->(org)
            WHERE LOWER(org.name) CONTAINS LOWER("key_term") OR LOWER(org.context) CONTAINS LOWER("key_term")
            RETURN person.name, person.source_context, type(r), org.name, org.source_context, person.chunk_id, org.chunk_id
            LIMIT 30

            ENTITY ROLE PATTERN - For "what was X's role" questions:
            MATCH (person)-[r]-(connected)
            WHERE LOWER(person.name) CONTAINS LOWER("key_term")
            RETURN person.name, person.source_context, type(r), connected.name, connected.source_context, labels(connected), person.chunk_id, connected.chunk_id
            LIMIT 40

            OPPOSITION PATTERN - For "who opposed/fought" questions:
            MATCH (a)-[r:OPPOSED|FOUGHT]-(b)
            WHERE LOWER(a.name) CONTAINS LOWER("key_term") OR LOWER(b.name) CONTAINS LOWER("key_term") OR LOWER(a.context) CONTAINS LOWER("key_term") OR LOWER(b.context) CONTAINS LOWER("key_term")
            RETURN a.name, a.source_context, type(r), b.name, b.source_context, a.chunk_id, b.chunk_id
            LIMIT 40

            BROAD EXPLORATION PATTERN - For complex/general questions:
            MATCH (a)-[r]-(b)
            WHERE LOWER(a.name) CONTAINS LOWER("key_term1") OR LOWER(b.name) CONTAINS LOWER("key_term1") OR LOWER(a.name) CONTAINS LOWER("key_term2") OR LOWER(b.name) CONTAINS LOWER("key_term2") OR LOWER(a.context) CONTAINS LOWER("key_term1") OR LOWER(b.context) CONTAINS LOWER("key_term2")
            RETURN a.name, a.source_context, type(r), b.name, b.source_context, a.chunk_id, b.chunk_id
            LIMIT 50

            RULES:
            - Extract 2-3 key terms from the question and search for ALL of them with OR
            - Search both n.name AND n.context fields to catch more results  
            - Always include chunk_id for both nodes in relationship queries
            - Use LIMIT 40-50 to get comprehensive results
            - When in doubt, use the PRIMARY PATTERN with multiple search terms

            Question: {question}

            EXAMPLES:

            Question: "Who led the Yugoslav Partisans?"
            Pattern: LEADERSHIP
            Query:
            MATCH (person:Person)-[r:LED|COMMANDED]->(org)
            WHERE LOWER(org.name) CONTAINS LOWER("partisans") OR LOWER(org.context) CONTAINS LOWER("yugoslav")
            RETURN person.name, person.source_context, type(r), org.name, org.source_context, person.chunk_id, org.chunk_id
            LIMIT 30

            Question: "What was Tito's role in Yugoslavia?"
            Pattern: ENTITY ROLE
            Query:
            MATCH (person)-[r]-(connected)
            WHERE LOWER(person.name) CONTAINS LOWER("tito")
            RETURN person.name, person.source_context, type(r), connected.name, connected.source_context, labels(connected), person.chunk_id, connected.chunk_id
            LIMIT 40

            Question: "Who opposed the German forces in Greece?"
            Pattern: OPPOSITION
            Query:
            MATCH (a)-[r:OPPOSED|FOUGHT]-(b)
            WHERE LOWER(a.name) CONTAINS LOWER("german") OR LOWER(b.name) CONTAINS LOWER("german") OR LOWER(a.context) CONTAINS LOWER("greece") OR LOWER(b.context) CONTAINS LOWER("forces")
            RETURN a.name, a.source_context, type(r), b.name, b.source_context, a.chunk_id, b.chunk_id
            LIMIT 40

            Generate a broad Cypher query using these patterns. Prioritize getting SOME results over getting nothing.

            Only return the Cypher query, nothing else.
            """
        )
        
        # Create custom QA prompt for answer generation
        qa_prompt = PromptTemplate.from_template(
            """
            You are an assistant that helps answer questions based on graph database results.
            
            Question: {question}
            Context from database: {context}
            
            Based on the retrieved information, provide a comprehensive answer and analysis.
            When analyzing claims or statements, calculate the following rates based on the evidence:
            
            - Claim Support Rate: Percentage of retrieved evidence that supports the claim (0.0-1.0)
            - Contradiction Rate: Percentage of retrieved evidence that contradicts the claim (0.0-1.0) 
            - Numeric Grounding Rate: Percentage of numeric facts/figures that can be verified from the evidence (0.0-1.0)
            
            Structure your response as JSON with the following format:
            {{
                "result": "Your comprehensive answer to the question",
                "claim_support_rate": 0.0,
                "contradiction_rate": 0.0,
                "numeric_grounding_rate": 0.0
            }}
            
            Return only valid JSON, nothing else.
            """
        )
        
        # Initialize GraphCypherQAChain using the client's graph and provided LLM
        self.cypher_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.client.get_graph(),
            verbose=True,
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
            cypher_prompt=cypher_prompt,
            qa_prompt=qa_prompt,
            validate_cypher=True
        )
    
    def retrieve_and_answer(self, question: str) -> dict[str, Any]:
        """
        Retrieve information from Neo4j graph and generate answer
        
        Args:
            question: Natural language question to answer
            
        Returns:
            Dictionary containing answer and intermediate steps
        """
        try:
            result = self.cypher_chain.invoke({"query": question})
            return {
                "answer": result["result"],
                "cypher_query": result.get("intermediate_steps", [{}])[0].get("query", ""),
                "context": result.get("intermediate_steps", [{}])[0].get("context", ""),
                "success": True
            }
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def decision_gate(self, claim_support_rate, contradiction_rate, numeric_grounding_rate):
        """
        Decision gate to determine response type based on evidence quality metrics
        
        Args:
            claim_support_rate: Percentage of evidence supporting the claim (0.0-1.0)
            contradiction_rate: Percentage of evidence contradicting the claim (0.0-1.0)
            numeric_grounding_rate: Percentage of numeric facts that can be verified (0.0-1.0)
        
        Returns:
            str: Decision type - "Answer", "Extractive-only", "Ask-clarify", "No-answer", "Refuse"
        """
        
        # High contradiction rate - refuse to answer
        if contradiction_rate > 0.5:
            return "Refuse"
        
        # High support with good grounding - provide full answer
        if claim_support_rate > 0.3 and numeric_grounding_rate > 0.3:
            return "Answer"
        
        # Moderate support with some grounding - provide extractive answer only
        if claim_support_rate > 0.3 and numeric_grounding_rate > 0.3:
            return "Extractive-only"
        
        # Low support but some evidence exists - ask for clarification
        if claim_support_rate > 0.2 or numeric_grounding_rate > 0.2:
            return "Ask-clarify"
        
        # Very low support and grounding - no answer available
        return "No-answer"
