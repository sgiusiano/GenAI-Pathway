"""
Customer Service Chain

This module contains the main LCEL chain that integrates all components
of the customer service agent system.
"""

import json
from typing import Dict, Any, Optional
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from ..components.query_analyzer import QueryAnalyzer
from ..components.response_generator import ResponseGenerator
from ..components.conversation_summarizer import ConversationSummarizer
from ..utils.validators import validate_query, validate_response
from ..utils.helpers import format_response_for_display


class CustomerServiceChain:
    """Main chain that integrates all customer service components."""
    
    def __init__(self):
        """Initialize the CustomerServiceChain."""
        self.query_analyzer = QueryAnalyzer()
        self.response_generator = ResponseGenerator()
        self.conversation_summarizer = ConversationSummarizer()
        
        # Build the complete chain using LCEL
        self.complete_chain = (
            # Step 1: Analyze the query
            RunnablePassthrough.assign(
                analysis=lambda x: self.query_analyzer.analyze_query(x["query"])
            )
            # Step 2: Prepare data for response generation
            | RunnableLambda(lambda x: {
                "original_query": x["query"],
                "analysis": x["analysis"]
            })
            # Step 3: Generate response based on analysis
            | RunnableLambda(lambda x: {
                **x,
                "response_data": self.response_generator.generate_response(
                    x["original_query"], 
                    x["analysis"]
                )
            })
            # Step 4: Create conversation summary
            | RunnableLambda(lambda x: {
                **x,
                "summary": self.conversation_summarizer.create_summary(
                    x["analysis"],
                    x["response_data"]["response"]
                )
            })
            # Step 5: Format final output
            | RunnableLambda(lambda x: {
                "query": x["original_query"],
                "response": x["response_data"]["response"].content,
                "summary": x["summary"],
                "metadata": {
                    "category": x["analysis"].query_category,
                    "urgency": x["analysis"].urgency_level,
                    "sentiment": x["analysis"].customer_sentiment,
                    "prompt_used": x["response_data"]["prompt_used"]
                }
            })
        )
    
    def process_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Process a customer query through the complete chain.
        
        Args:
            query: The customer's query string
            
        Returns:
            Dictionary containing the response and conversation summary,
            or None if processing failed
        """
        try:
            # Validate input
            is_valid, error_message = validate_query(query)
            if not is_valid:
                print(f"❌ Invalid query: {error_message}")
                return None
            
            # Process through the chain
            result = self.complete_chain.invoke({"query": query})
            
            # Validate output
            is_valid, error_message = validate_response(result)
            if not is_valid:
                print(f"❌ Invalid response: {error_message}")
                return None
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            return None
    
    def batch_process(self, queries: list[str]) -> list[Dict[str, Any]]:
        """
        Process multiple queries in batch.
        
        Args:
            queries: List of customer query strings
            
        Returns:
            List of processed results
        """
        results = []
        for query in queries:
            try:
                result = self.process_query(query)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Warning: Failed to process query '{query[:50]}...': {str(e)}")
                continue
        
        return results
    
    def get_chain_info(self) -> Dict[str, Any]:
        """
        Get information about the chain structure.
        
        Returns:
            Dictionary with chain information
        """
        return {
            "components": [
                "QueryAnalyzer",
                "ResponseGenerator", 
                "ConversationSummarizer"
            ],
            "steps": [
                "Query Analysis",
                "Response Generation",
                "Conversation Summarization",
                "Output Formatting"
            ],
            "input_schema": {
                "query": "string (required)"
            },
            "output_schema": {
                "query": "string",
                "response": "string", 
                "summary": "ConversationSummary",
                "metadata": "dict"
            }
        }
    
    def test_chain(self, test_query: str = "Hello, I need help with my order") -> bool:
        """
        Test the chain with a simple query.
        
        Args:
            test_query: A test query string
            
        Returns:
            True if test passes, False otherwise
        """
        try:
            result = self.process_query(test_query)
            if result and "response" in result and "summary" in result:
                print("✅ Chain test passed!")
                return True
            else:
                print("❌ Chain test failed: Invalid output structure")
                return False
        except Exception as e:
            print(f"❌ Chain test failed: {str(e)}")
            return False
    
    def format_response_for_display(self, result: Dict[str, Any]) -> str:
        """
        Formats the chain result for display purposes.
        
        Args:
            result: The chain result dictionary
            
        Returns:
            Formatted string representation
        """
        return format_response_for_display(result) 