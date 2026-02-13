"""
Customer Service Agent with LangChain

A multi-component customer service agent using LangChain Expression Language (LCEL),
structured outputs with Pydantic, and LangSmith for observability.
"""

__version__ = "1.0.0"
__author__ = "GenAI Pathway Mentoring"
__description__ = "Advanced Customer Service Agent with LangChain"

from .models import ExtractedEntities, QueryAnalysis, ConversationSummary
from .components import QueryAnalyzer, ResponseGenerator, ConversationSummarizer
from .chains import CustomerServiceChain

__all__ = [
    "ExtractedEntities",
    "QueryAnalysis", 
    "ConversationSummary",
    "QueryAnalyzer",
    "ResponseGenerator",
    "ConversationSummarizer",
    "CustomerServiceChain"
] 