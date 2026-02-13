from typing import Any
from datetime import datetime
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig

from ..memory.hybrid_memory import HybridMemory, conversationMessage
from ..tools.customer_tools import customerTools
from ..config.llm_config import llm_config


class MemoryAgent:
    """
    MemoryAgent combines memory management with tool usage for contextual customer service.
    
    This agent:
    - Maintains conversation memory for different customers
    - Uses tools to gather current information  
    - Provides personalized responses based on customer history
    - Implements session management for different customers
    """
    
    def __init__(self):
        """Initialize the MemoryAgent with memory, tools, and LLM configuration."""
        self.customer_sessions: dict[str, HybridMemory] = {}
        self.tools = self._initialize_tools()
        self.llm = llm_config.llm
        self.agent_executor = self._create_agent()

    def _initialize_tools(self) -> list[BaseTool]:
        """Initialize and return the list of available tools."""
        tools = [
            customerTools.get_customer_info,
            customerTools.get_order_status,
            customerTools.get_shipping_tracking,
            customerTools.get_customer_tickets
        ]
        return tools
    
    def _create_agent_prompt(self) -> PromptTemplate:
        """Create the custom prompt for the memory-aware agent."""
        prompt_template = """You are a helpful customer service agent with access to conversation memory and customer tools.

Your primary responsibilities:
1. Use conversation memory to maintain context and continuity across interactions
2. Select appropriate tools based on user queries to gather current information
3. Provide personalized responses that reference previous interactions when relevant
4. Be proactive in using tools to help customers

MEMORY CONTEXT:
{memory_context}

AVAILABLE TOOLS:
{tools}

TOOL NAMES:
{tool_names}

When responding:
- Always check memory context first to understand the customer's history
- Use tools to gather up-to-date information when needed
- Reference previous conversations naturally in your responses
- Be conversational and helpful while maintaining professionalism
- If you need customer information, use the get_customer_info tool with their email
- For order-related queries, use order status and shipping tracking tools
- For support issues, check customer tickets

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        return PromptTemplate(
            template=prompt_template,
            input_variables=["memory_context", "tools", "tool_names", "input", "agent_scratchpad"]
        )
    
    def _create_agent(self) -> AgentExecutor:
        """Create the ReAct agent with memory-aware prompt and tools."""
        prompt = self._create_agent_prompt()
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        return agent_executor
    
    def _get_or_create_session(self, customer_email: str) -> HybridMemory:
        """Get existing session or create new one for customer."""
        if customer_email not in self.customer_sessions:
            self.customer_sessions[customer_email] = HybridMemory()
        return self.customer_sessions[customer_email]
    
    def _store_interaction(self, customer_email: str, user_query: str, agent_response: str) -> None:
        """Store the interaction in customer's memory."""
        memory = self._get_or_create_session(customer_email)
        
        # Store user message
        user_message = conversationMessage(
            role="User",
            content=user_query,
            metadata={"email": customer_email}
        )
        memory.manage_conversation_buffer(user_message)
        
        # Store agent response
        agent_message = conversationMessage(
            role="Assistant", 
            content=agent_response,
            metadata={"email": customer_email}
        )
        memory.manage_conversation_buffer(agent_message)
    
    def process_query(self, customer_email: str, user_query: str) -> str:
        """
        Process a user query with memory context and tool usage.
        
        Args:
            customer_email: Email of the customer for session management
            user_query: The customer's question or request
            
        Returns:
            Agent's response incorporating memory and tool results
        """
        # Load conversation memory and customer context
        memory = self._get_or_create_session(customer_email)
        memory_context = memory.memoryRetrieval()
        
        # Prepare agent input with memory context
        agent_input = {
            "memory_context": memory_context,
            "input": f"Customer Email: {customer_email}\nQuery: {user_query}"
        }
        
        # Execute agent with tools and memory
        try:
            result = self.agent_executor.invoke(agent_input)
            agent_response = result.get("output", "I apologize, but I couldn't process your request properly.")
            
            # Store the interaction in memory
            self._store_interaction(customer_email, user_query, agent_response)
            
            return agent_response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error while processing your request: {str(e)}"
            self._store_interaction(customer_email, user_query, error_response)
            return error_response
    
    def get_customer_conversation_history(self, customer_email: str) -> str:
        """
        Retrieve the conversation history for a specific customer.
        
        Args:
            customer_email: Email of the customer
            
        Returns:
            Formatted conversation history
        """
        if customer_email in self.customer_sessions:
            memory = self.customer_sessions[customer_email]
            return memory.memoryRetrieval()
        return f"No conversation history found for {customer_email}"
    
    def clear_customer_session(self, customer_email: str) -> bool:
        """
        Clear the conversation session for a specific customer.
        
        Args:
            customer_email: Email of the customer
            
        Returns:
            True if session was cleared, False if no session existed
        """
        if customer_email in self.customer_sessions:
            del self.customer_sessions[customer_email]
            return True
        return False
    
    def get_active_sessions(self) -> list[str]:
        """
        Get list of active customer email sessions.

        Returns:
            List of customer emails with active sessions
        """
        return list(self.customer_sessions.keys())
