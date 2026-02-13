"""
Conversation summary models for customer service

This module contains models for summarizing customer service interactions.
"""

from typing import List, Literal
from pydantic import BaseModel, Field
from .entities import ExtractedEntities


class ConversationSummary(BaseModel):
    """A structured summary of the customer service interaction."""
    
    timestamp: str = Field(
        description="Timestamp of the interaction in ISO format"
    )
    customer_id: str = Field(
        default="auto_generated", 
        description="Customer identifier"
    )
    conversation_summary: str = Field(
        description="A concise, one-sentence summary of the interaction"
    )
    query_category: str = Field(
        description="Category of the customer query"
    )
    customer_sentiment: str = Field(
        description="Customer sentiment during the interaction"
    )
    urgency_level: str = Field(
        description="Urgency level of the query"
    )
    mentioned_products: List[str] = Field(
        description="List of products mentioned in the conversation"
    )
    extracted_information: ExtractedEntities = Field(
        description="Key entities extracted from the conversation"
    )
    resolution_status: Literal["resolved", "pending", "escalated"] = Field(
        description="Current status of the query resolution"
    )
    actions_taken: List[str] = Field(
        description="List of actions the agent took or suggested"
    )
    follow_up_required: bool = Field(
        description="Whether follow-up is required for this interaction"
    )