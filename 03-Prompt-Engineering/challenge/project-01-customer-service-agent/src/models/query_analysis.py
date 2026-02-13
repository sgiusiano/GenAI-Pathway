"""
Query analysis models for customer service

This module contains models for analyzing and classifying customer queries.
"""

from typing import Literal
from pydantic import BaseModel, Field
from .entities import ExtractedEntities


class QueryAnalysis(BaseModel):
    """Analyzes and classifies a customer query."""
    
    query_category: Literal[
        "technical_support", 
        "billing", 
        "returns", 
        "product_inquiry", 
        "general_information"
    ] = Field(
        description="Category of the customer query"
    )
    urgency_level: Literal["low", "medium", "high"] = Field(
        description="Urgency level of the query based on customer language and needs"
    )
    customer_sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="Detected customer sentiment from their message"
    )
    entities: ExtractedEntities = Field(
        description="Key entities extracted from the query"
    )