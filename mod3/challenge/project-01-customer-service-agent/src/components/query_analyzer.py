"""
Query Analyzer Component

This module contains the query analysis component that classifies and extracts
information from customer queries.
"""

from typing import Any
from langchain_core.runnables import RunnableLambda
from ..models.query_analysis import QueryAnalysis
from ..prompts.analysis_prompts import analysis_prompt
from ..config.llm_config import llm_config
from ..utils.validators import validate_query, sanitize_input


class QueryAnalyzer:
    """Component for analyzing and classifying customer queries."""
    
    def __init__(self):
        """Initialize the QueryAnalyzer component."""
        self.llm = llm_config.llm.with_structured_output(QueryAnalysis)
        self.chain = analysis_prompt | self.llm
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyzes a customer query and returns structured information.
        
        Args:
            query: The customer query string
            
        Returns:
            QueryAnalysis object with classification and extracted entities
            
        Raises:
            ValueError: If the query is invalid
        """
        # Validate and sanitize input
        is_valid, error_message = validate_query(query)
        if not is_valid:
            raise ValueError(f"Invalid query: {error_message}")
        
        sanitized_query = sanitize_input(query)
        
        # Analyze the query
        try:
            result = self.chain.invoke({"query": sanitized_query})
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to analyze query: {str(e)}")
    
    def batch_analyze(self, queries: list[str]) -> list[QueryAnalysis]:
        """
        Analyzes multiple queries in batch.
        
        Args:
            queries: List of customer query strings
            
        Returns:
            List of QueryAnalysis objects
        """
        results = []
        for query in queries:
            try:
                analysis = self.analyze_query(query)
                results.append(analysis)
            except Exception as e:
                # Log error and continue with next query
                print(f"Warning: Failed to analyze query '{query[:50]}...': {str(e)}")
                continue
        
        return results
    
    def get_analysis_summary(self, analysis: QueryAnalysis) -> dict[str, Any]:
        """
        Creates a summary of the analysis results.
        
        Args:
            analysis: QueryAnalysis object
            
        Returns:
            Dictionary with summary information
        """
        return {
            "category": analysis.query_category,
            "urgency": analysis.urgency_level,
            "sentiment": analysis.customer_sentiment,
            "entities": {
                "product": analysis.entities.product_name,
                "order_number": analysis.entities.order_number,
                "date": analysis.entities.date
            }
        } 