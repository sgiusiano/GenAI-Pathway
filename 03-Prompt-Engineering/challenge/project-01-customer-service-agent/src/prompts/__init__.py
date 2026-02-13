"""
Prompt templates for the Customer Service Agent

This module contains all prompt templates organized by function.
"""

from .analysis_prompts import analysis_prompt
from .response_prompts import (
    technical_support_prompt,
    billing_prompt,
    returns_prompt,
    product_inquiry_prompt,
    general_prompt
)
from .summary_prompts import summary_prompt

__all__ = [
    "analysis_prompt",
    "technical_support_prompt",
    "billing_prompt", 
    "returns_prompt",
    "product_inquiry_prompt",
    "general_prompt",
    "summary_prompt"
] 