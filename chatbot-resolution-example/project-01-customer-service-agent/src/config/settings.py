"""
Configuration settings for the Customer Service Agent

This module handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # LangSmith Configuration
    langsmith_api_key: Optional[str] = Field(None, env="LANGSMITH_API_KEY")
    langsmith_project: Optional[str] = Field(None, env="LANGSMITH_PROJECT")
    langsmith_tracing: bool = Field(default=True, env="LANGSMITH_TRACING")
    
    # Application Configuration
    app_name: str = Field(default="Customer Service Agent", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    ## Example of use case settings

    # Company Information
    company_name: str = Field(default="TechStore Plus", env="COMPANY_NAME")
    company_location: str = Field(default="New York, USA", env="COMPANY_LOCATION")
    
    # Return Policy Configuration
    return_window_days: int = Field(default=30, env="RETURN_WINDOW_DAYS")
    refund_processing_days: int = Field(default=5, env="REFUND_PROCESSING_DAYS")
    
# Global settings instance
settings = Settings()

# Validate required settings for production
if not settings.openai_api_key:
    print("Warning: OPENAI_API_KEY not set. Some features may not work properly.")
    print("Please set OPENAI_API_KEY in your environment variables or .env file.") 