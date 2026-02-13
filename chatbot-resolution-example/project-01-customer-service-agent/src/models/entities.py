"""
Entity extraction models for customer queries

This module contains models for extracting structured information from customer queries.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ExtractedEntities(BaseModel):
    """Entities extracted from customer queries."""
    
    product_name: Optional[str] = Field(
        None, 
        description="The specific product mentioned by the user"
    )
    order_number: Optional[str] = Field(
        None, 
        description="The order number mentioned by the user (e.g., TEC-2024001)"
    )
    date: Optional[str] = Field(
        None, 
        description="Any date mentioned in the query"
    )