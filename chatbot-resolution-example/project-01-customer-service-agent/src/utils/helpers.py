"""
Helper functions for the Customer Service Agent

This module contains utility functions used throughout the system.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from ..models.query_analysis import QueryAnalysis
from ..models.conversation_summary import ConversationSummary


def create_conversation_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a structured summary of the customer service interaction.
    
    Args:
        data: Dictionary containing analysis and response information
        
    Returns:
        Dictionary with complete conversation summary data
    """
    analysis = data["analysis"]
    response = data["response"]
    
    # Extract mentioned products
    mentioned_products = []
    if analysis.entities.product_name:
        mentioned_products.append(analysis.entities.product_name)
    
    # Determine resolution status based on urgency and sentiment
    resolution_status = "resolved"  # Default
    if analysis.urgency_level == "high":
        resolution_status = "escalated"
    elif analysis.customer_sentiment == "negative":
        resolution_status = "pending"
    
    # Determine if follow-up is required
    follow_up_required = (
        analysis.urgency_level == "high" or 
        analysis.customer_sentiment == "negative"
    )
    
    # Create conversation summary
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "customer_id": "auto_generated",
        "conversation_summary": f"Customer inquired about {analysis.query_category.replace('_', ' ')} with {analysis.customer_sentiment} sentiment",
        "query_category": analysis.query_category,
        "customer_sentiment": analysis.customer_sentiment,
        "urgency_level": analysis.urgency_level,
        "mentioned_products": mentioned_products,
        "extracted_information": {
            "product_name": analysis.entities.product_name,
            "order_number": analysis.entities.order_number,
            "date": analysis.entities.date
        },
        "resolution_status": resolution_status,
        "actions_taken": [
            f"Provided {analysis.query_category.replace('_', ' ')} assistance",
            "Analyzed customer query and sentiment",
            "Generated personalized response"
        ],
        "follow_up_required": follow_up_required,
        "agent_response": response.content
    }
    
    return summary_data


def route_to_prompt(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Routes the query to the appropriate prompt based on its category.
    
    Args:
        data: Dictionary containing 'analysis' and 'original_query'
        
    Returns:
        Dictionary with analysis, query, and formatted prompt
    """
    from ..prompts.response_prompts import (
        technical_support_prompt,
        billing_prompt,
        returns_prompt,
        product_inquiry_prompt,
        general_prompt
    )
    
    analysis = data["analysis"]
    category = analysis.query_category
    
    # Create routing dictionary
    prompt_router = {
        "technical_support": technical_support_prompt,
        "billing": billing_prompt,
        "returns": returns_prompt,
        "product_inquiry": product_inquiry_prompt,
        "general_information": general_prompt
    }
    
    # Prepare data for the prompt template
    prompt_data = {
        "original_query": data["original_query"],
        "customer_sentiment": analysis.customer_sentiment,
        "urgency_level": analysis.urgency_level,
        "product_name": analysis.entities.product_name or "Not specified",
        "order_number": analysis.entities.order_number or "Not specified",
        "date": analysis.entities.date or "Not specified"
    }
    
    # Select and format the appropriate prompt
    selected_prompt = prompt_router.get(category, general_prompt)
    formatted_messages = selected_prompt.format_messages(**prompt_data)
    
    return {
        "analysis": analysis,
        "original_query": data["original_query"],
        "prompt_used": category,
        "messages": formatted_messages
    }


def format_response_for_display(response_data: Dict[str, Any]) -> str:
    """
    Formats the response data for display purposes.
    
    Args:
        response_data: Dictionary containing response information
        
    Returns:
        Formatted string representation
    """
    if not response_data:
        return "❌ No response data available"
    
    formatted = []
    formatted.append("🤖 AGENT RESPONSE:")
    formatted.append(f"{response_data.get('response', 'No response')}")
    
    if 'summary' in response_data:
        summary = response_data['summary']
        formatted.append("\n📊 CONVERSATION SUMMARY:")
        formatted.append(f"- Category: {summary.query_category}")
        formatted.append(f"- Sentiment: {summary.customer_sentiment}")
        formatted.append(f"- Urgency: {summary.urgency_level}")
        formatted.append(f"- Status: {summary.resolution_status}")
        formatted.append(f"- Follow-up Required: {summary.follow_up_required}")
    
    return "\n".join(formatted) 