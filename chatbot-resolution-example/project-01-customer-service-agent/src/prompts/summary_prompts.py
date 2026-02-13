"""
Summary prompts for conversation logging

This module contains prompt templates for summarizing customer service interactions.
"""

from langchain_core.prompts import ChatPromptTemplate


# Conversation summary generation prompt
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", """Generate a structured summary of this customer service interaction.
    
    Conversation data:
    {conversation_data}
    
    Create a complete and accurate ConversationSummary."""),
    ("human", "Please generate the conversation summary.")
]) 