"""
Conversation Summarizer Component

This module contains the conversation summarization component that creates
structured summaries of customer service interactions.
"""

import json
from typing import Any
from langchain_core.runnables import RunnableLambda
from ..models.conversation_summary import ConversationSummary
from ..prompts.summary_prompts import summary_prompt
from ..config.llm_config import llm_config
from ..utils.helpers import create_conversation_summary


class ConversationSummarizer:
    """Component for summarizing customer service conversations."""
    
    def __init__(self):
        """Initialize the ConversationSummarizer component."""
        self.llm = llm_config.llm.with_structured_output(ConversationSummary)
        self.summary_chain = summary_prompt | self.llm
    
    def create_summary(self, analysis_data: dict[str, Any], response_data: dict[str, Any]) -> ConversationSummary:
        """
        Creates a structured summary of the conversation.
        
        Args:
            analysis_data: Dictionary containing query analysis
            response_data: Dictionary containing response information
            
        Returns:
            ConversationSummary object
        """
        try:
            # Create the initial summary data
            summary_data = create_conversation_summary({
                "analysis": analysis_data,
                "response": response_data
            })
            
            # Generate the final structured summary using LLM
            result = self.summary_chain.invoke({
                "conversation_data": json.dumps(summary_data, indent=2)
            })
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to create conversation summary: {str(e)}")
    
    def batch_summarize(self, conversations: list[dict[str, Any]]) -> list[ConversationSummary]:
        """
        Creates summaries for multiple conversations.
        
        Args:
            conversations: List of conversation data dictionaries
            
        Returns:
            List of ConversationSummary objects
        """
        summaries = []
        for conversation in conversations:
            try:
                summary = self.create_summary(
                    conversation.get("analysis"),
                    conversation.get("response")
                )
                summaries.append(summary)
            except Exception as e:
                print(f"Warning: Failed to summarize conversation: {str(e)}")
                continue
        
        return summaries
    
    def get_summary_statistics(self, summaries: list[ConversationSummary]) -> dict[str, Any]:
        """
        Generates statistics from a list of conversation summaries.
        
        Args:
            summaries: List of ConversationSummary objects
            
        Returns:
            Dictionary with summary statistics
        """
        if not summaries:
            return {}
        
        # Count categories
        categories = {}
        sentiments = {}
        urgency_levels = {}
        resolution_statuses = {}
        follow_up_count = 0
        
        for summary in summaries:
            # Category counts
            categories[summary.query_category] = categories.get(summary.query_category, 0) + 1
            
            # Sentiment counts
            sentiments[summary.customer_sentiment] = sentiments.get(summary.customer_sentiment, 0) + 1
            
            # Urgency level counts
            urgency_levels[summary.urgency_level] = urgency_levels.get(summary.urgency_level, 0) + 1
            
            # Resolution status counts
            resolution_statuses[summary.resolution_status] = resolution_statuses.get(summary.resolution_status, 0) + 1
            
            # Follow-up count
            if summary.follow_up_required:
                follow_up_count += 1
        
        return {
            "total_conversations": len(summaries),
            "categories": categories,
            "sentiments": sentiments,
            "urgency_levels": urgency_levels,
            "resolution_statuses": resolution_statuses,
            "follow_up_required": follow_up_count,
            "follow_up_percentage": (follow_up_count / len(summaries)) * 100
        }
    
    def export_summaries(self, summaries: list[ConversationSummary], format: str = "json") -> str:
        """
        Exports conversation summaries in various formats.
        
        Args:
            summaries: List of ConversationSummary objects
            format: Export format ("json", "csv", "txt")
            
        Returns:
            String representation of the exported data
        """
        if format.lower() == "json":
            return json.dumps([summary.dict() for summary in summaries], indent=2)
        
        elif format.lower() == "txt":
            lines = []
            for i, summary in enumerate(summaries, 1):
                lines.append(f"Conversation {i}:")
                lines.append(f"  Category: {summary.query_category}")
                lines.append(f"  Sentiment: {summary.customer_sentiment}")
                lines.append(f"  Urgency: {summary.urgency_level}")
                lines.append(f"  Status: {summary.resolution_status}")
                lines.append(f"  Follow-up Required: {summary.follow_up_required}")
                lines.append("")
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}") 