"""
LLM configuration and initialization for the Customer Service Agent

This module handles the setup and configuration of language models.
"""

from langchain_openai import ChatOpenAI
from .settings import settings


class LLMConfig:
    """Configuration class for Language Models."""
    
    def __init__(self):
        """Initialize LLM configuration."""
        self._llm = None
        self._llm_analyzer = None
        self._llm_summarizer = None
    
    @property
    def llm(self) -> ChatOpenAI:
        """Get the main LLM instance."""
        if self._llm is None:
            if not settings.openai_api_key:
                raise ValueError(
                    "OpenAI API key is required. Please set OPENAI_API_KEY environment variable."
                )
            self._llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                api_key=settings.openai_api_key
            )
        return self._llm
    
    @property
    def llm_analyzer(self) -> ChatOpenAI:
        """Get the LLM instance configured for analysis."""
        if self._llm_analyzer is None:
            self._llm_analyzer = self.llm.with_structured_output(
                "QueryAnalysis"  # This will be imported from models
            )
        return self._llm_analyzer
    
    @property
    def llm_summarizer(self) -> ChatOpenAI:
        """Get the LLM instance configured for summarization."""
        if self._llm_summarizer is None:
            self._llm_summarizer = self.llm.with_structured_output(
                "ConversationSummary"  # This will be imported from models
            )
        return self._llm_summarizer


# Global LLM configuration instance
llm_config = LLMConfig() 