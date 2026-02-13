"""
Demo script for the MemoryAgent class.

This script demonstrates the key features of the MemoryAgent:
- Memory management across conversations
- Tool usage for current information
- Session management for different customers
- Contextual responses based on conversation history
"""

import os
from src.agent.memory_agent import MemoryAgent

def demo_memory_agent():
    """Demonstrate the MemoryAgent functionality."""
    
    # Initialize the agent
    print("🤖 Initializing MemoryAgent...")
    agent = MemoryAgent()
    print("✅ MemoryAgent initialized successfully!\n")
    
    # Demo customer emails
    customer1 = "john.smith@email.com"
    customer2 = "sarah.johnson@email.com"
    
    print("=" * 60)
    print("DEMO: Memory-Aware Customer Service Agent")
    print("=" * 60)
    
    # Scenario 1: First interaction with Customer 1
    print(f"\n📧 Customer: {customer1}")
    print("Query: Hello, I'd like to check my account information")
    print("\n🤖 Agent Response:")
    response1 = agent.process_query(
        customer1, 
        "Hello, I'd like to check my account information"
    )
    print(response1)
    
    # Scenario 2: Follow-up question from Customer 1 (should reference previous interaction)
    print(f"\n📧 Customer: {customer1}")
    print("Query: What about my recent orders?")
    print("\n🤖 Agent Response:")
    response2 = agent.process_query(
        customer1,
        "What about my recent orders?"
    )
    print(response2)
    
    # Scenario 3: Different customer with similar query
    print(f"\n📧 Customer: {customer2}")
    print("Query: Hello, I'd like to check my account information")
    print("\n🤖 Agent Response:")
    response3 = agent.process_query(
        customer2,
        "Hello, I'd like to check my account information"
    )
    print(response3)
    
    # Scenario 4: Customer 1 returns - agent should remember context
    print(f"\n📧 Customer: {customer1} (returning)")
    print("Query: I'm having issues with my laptop order")
    print("\n🤖 Agent Response:")
    response4 = agent.process_query(
        customer1,
        "I'm having issues with my laptop order"
    )
    print(response4)
    
    # Scenario 5: Customer Recognition & Context
    print(f"\n📧 Customer: john.doe@company.com")
    print("Query: Hello, I'm john.doe@company.com")
    print("\n🤖 Agent Response:")
    response5 = agent.process_query(
        "john.doe@company.com",
        "Hello, I'm john.doe@company.com"
    )
    print(response5)
    
    # Scenario 6: Order Status Inquiry
    print(f"\n📧 Customer: john.doe@company.com")
    print("Query: What's the status of my order TEC-2024-001?")
    print("\n🤖 Agent Response:")
    response6 = agent.process_query(
        "john.doe@company.com",
        "What's the status of my order TEC-2024-001?"
    )
    print(response6)
    
    # Show memory management features
    print("\n" + "=" * 60)
    print("MEMORY MANAGEMENT FEATURES")
    print("=" * 60)
    
    # Show active sessions
    print(f"\n🗂️  Active customer sessions: {agent.get_active_sessions()}")
    
    # Show conversation history for customer 1
    print(f"\n📚 Conversation history for {customer1}:")
    print(agent.get_customer_conversation_history(customer1))
    
    # Demonstrate session clearing
    print(f"\n🗑️  Clearing session for {customer2}...")
    cleared = agent.clear_customer_session(customer2)
    print(f"Session cleared: {cleared}")
    print(f"Active sessions after clearing: {agent.get_active_sessions()}")

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: Please set your OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    try:
        demo_memory_agent()
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("\nNote: Make sure you have installed all requirements:")
        print("pip install -r requirements.txt")