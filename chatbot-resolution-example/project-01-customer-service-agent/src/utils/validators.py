"""
Validation functions for the Customer Service Agent

This module contains validation utilities for queries and responses.
"""

import re
from typing import Dict, Any, Optional, Tuple


def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validates a customer query string.
    
    Args:
        query: The customer query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query.strip()) < 5:
        return False, "Query must be at least 5 characters long"
    
    if len(query) > 1000:
        return False, "Query cannot exceed 1000 characters"
    
    # Check for potentially harmful content
    harmful_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'data:text/html',
        r'vbscript:'
    ]
    
    for pattern in harmful_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False, "Query contains potentially harmful content"
    
    return True, None


def validate_response(response_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates the response data structure.
    
    Args:
        response_data: The response data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['response', 'summary']
    
    for field in required_fields:
        if field not in response_data:
            return False, f"Missing required field: {field}"
    
    if not response_data['response']:
        return False, "Response content cannot be empty"
    
    if not response_data['summary']:
        return False, "Summary cannot be empty"
    
    return True, None


def validate_order_number(order_number: str) -> bool:
    """
    Validates the format of an order number.
    
    Args:
        order_number: The order number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not order_number:
        return False
    
    # Expected format: TEC-YYYYNNN
    pattern = r'^TEC-\d{7}$'
    return bool(re.match(pattern, order_number))


def sanitize_input(text: str) -> str:
    """
    Sanitizes input text to prevent injection attacks.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove script-like content
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def validate_urgency_level(urgency: str) -> bool:
    """
    Validates urgency level values.
    
    Args:
        urgency: The urgency level to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_levels = ['low', 'medium', 'high']
    return urgency.lower() in valid_levels


def validate_sentiment(sentiment: str) -> bool:
    """
    Validates sentiment values.
    
    Args:
        sentiment: The sentiment to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_sentiments = ['positive', 'neutral', 'negative']
    return sentiment.lower() in valid_sentiments 