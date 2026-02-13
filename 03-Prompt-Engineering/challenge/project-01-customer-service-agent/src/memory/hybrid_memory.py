from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.memory import BaseMemory
from langchain_openai import ChatOpenAI

class conversationMessage(BaseModel):
    """Represents a single conversation message."""
    role: Literal["User", "Assistant"] = Field(description="Role of the message sender")
    content: str = Field(description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] | None = Field(default_factory=dict)

class HybridMemory(BaseModel):
    """Hybrid memory system combining buffer and summary approaches using native LangChain patterns"""
    conversation_buffer: list[conversationMessage] = Field(default_factory=list)
    conversation_summary: str = Field(default="", description="Summary of older conversations")
    max_buffer_size: int = Field(default=5, description="Maximum messages to keep in buffer")
    customer_context: dict[str, Any] = Field(default_factory=dict)

    def _format_messages(self, messages: list[conversationMessage]) -> str:
        """
        Private method to format conversation messages into a readable text format.
        
        Args:
            messages: List of conversationMessage objects to format
            
        Returns:
            str: Formatted conversation text
        """
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(f"{msg.role}: {msg.content}")
        return "\n".join(formatted_messages)
    
    def _extract_customer_context(self, message: conversationMessage) -> None:
        """
        Private method to extract relevant customer context from message metadata
        and store it in customer_context field.
        
        Args:
            message: The conversationMessage to extract context from
        """
        if not message.metadata:
            return
            
        # Define relevant context keys to extract
        relevant_keys = [
            'email', 'preferences', 'previous_issues'
        ]
        
        # Extract relevant context from metadata
        for key, value in message.metadata.items():
            # Check if the key is relevant for customer context
            if any(relevant_key in key.lower() for relevant_key in relevant_keys):
                # Update customer context, preserving existing data
                if key not in self.customer_context or value:
                    self.customer_context[key] = value

    def _generate_summary(self) -> str:
        """
        Private method to generate a summary of all messages in the buffer using LangChain LCEL.
        
        Returns:
            str: Generated summary of the conversation buffer
        """
        if not self.conversation_buffer:
            return ""
        
        # Format messages for the prompt
        conversation_text = self._format_messages(self.conversation_buffer)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(
            """Please provide a concise summary of the following conversation between a User and Assistant.
            Focus on key topics discussed, important information shared, and any decisions or conclusions reached.
            
            Conversation:
            {conversation}
            
            Summary:"""
        )
        
        # Create the LLM
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # Create the chain using LCEL
        chain = prompt | llm | StrOutputParser()
        
        # Generate and return the summary
        summary = chain.invoke({"conversation": conversation_text})
        return summary
    
    def manage_conversation_buffer(self, message: conversationMessage) -> None:
        """
        Manages the conversation buffer by adding new messages and removing older ones
        when the buffer size exceeds max_buffer_size. Also extracts customer context
        from message metadata.
        
        Args:
            message: The conversationMessage to add to the buffer
        """
        # Extract customer context from message metadata
        self._extract_customer_context(message)
        
        # Add the new message to the buffer
        self.conversation_buffer.append(message)
        
        # Check if buffer size exceeds maximum
        if len(self.conversation_buffer) > self.max_buffer_size:
            # Generate summary before clearing older entries
            new_summary = self._generate_summary()
            # Append to existing summary if it exists
            if self.conversation_summary:
                self.conversation_summary += "\n\n ****New Summary**** \n" + new_summary #I decided to keep all old summaries
            else:
                self.conversation_summary = new_summary
            
            # Clear all older entries, keep only the most recent message
            self.conversation_buffer = [self.conversation_buffer[-1]]
    
    def memoryRetrieval(self) -> str:
        """
        Retrieves and formats all memory context for LLM consumption.
        
        Returns:
            str: Formatted memory context including conversation summary,
                 current buffer, and customer context
        """
        formatted_context = []
        
        # Add conversation summary if it exists
        if self.conversation_summary.strip():
            formatted_context.append("## Previous Conversation Summary:")
            formatted_context.append(self.conversation_summary)
            formatted_context.append("")
        
        # Add current conversation buffer
        if self.conversation_buffer:
            formatted_context.append("## Current Conversation:")
            current_conversation = self._format_messages(self.conversation_buffer)
            formatted_context.append(current_conversation)
            formatted_context.append("")
        
        # Add customer context if it exists
        if self.customer_context:
            formatted_context.append("## Customer Context:")
            for key, value in self.customer_context.items():
                formatted_context.append(f"- {key}: {value}")
            formatted_context.append("")
        
        return "\n".join(formatted_context).strip()
