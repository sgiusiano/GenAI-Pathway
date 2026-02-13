"""
Response Generator Component

This module contains the response generation component that creates
context-aware responses based on query analysis.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableLambda
from ..models.query_analysis import QueryAnalysis
from ..prompts.response_prompts import (
    technical_support_prompt,
    billing_prompt,
    returns_prompt,
    product_inquiry_prompt,
    general_prompt
)
from ..config.llm_config import llm_config
from ..utils.helpers import route_to_prompt


class ResponseGenerator:
    """Component for generating context-aware customer service responses."""
    
    def __init__(self):
        """Initialize the ResponseGenerator component."""
        self.llm = llm_config.llm
        self.prompt_router = {
            "technical_support": technical_support_prompt,
            "billing": billing_prompt,
            "returns": returns_prompt,
            "product_inquiry": product_inquiry_prompt,
            "general_information": general_prompt
        }
        
        # Create the response generation chain
        self.response_chain = (
            RunnableLambda(route_to_prompt) 
            | RunnableLambda(lambda x: {
                **x,
                "response": self.llm.invoke(x["messages"])
            })
        )
    
    def generate_response(self, query: str, analysis: QueryAnalysis) -> Dict[str, Any]:
        """
        Generates a response based on the query analysis.
        
        Args:
            query: The original customer query
            analysis: QueryAnalysis object with classification
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Prepare data for the chain
            chain_input = {
                "original_query": query,
                "analysis": analysis
            }
            
            # Generate response
            result = self.response_chain.invoke(chain_input)
            
            return {
                "response": result["response"],
                "prompt_used": result["prompt_used"],
                "analysis": analysis
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {str(e)}")
    
    def get_prompt_for_category(self, category: str):
        """
        Gets the appropriate prompt template for a query category.
        
        Args:
            category: The query category
            
        Returns:
            The corresponding prompt template
        """
        return self.prompt_router.get(category, general_prompt)
    
    def customize_response_prompt(self, category: str, custom_instructions: str):
        """
        Customizes the response prompt for a specific category.
        
        Args:
            category: The query category
            prompt: The custom prompt template
            
        Returns:
            None
        """
        if category in self.prompt_router:
            # Create a new prompt with custom instructions
            base_prompt = self.prompt_router[category]
            # This would require more complex prompt manipulation
            # For now, we'll just log the customization
            print(f"Customizing prompt for category: {category}")
    
    def get_response_metadata(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts metadata from the response data.
        
        Args:
            response_data: The response data dictionary
            
        Returns:
            Dictionary with metadata
        """
        return {
            "category": response_data.get("prompt_used"),
            "response_length": len(response_data.get("response", {}).get("content", "")),
            "timestamp": response_data.get("timestamp"),
            "analysis_summary": response_data.get("analysis")
        } 