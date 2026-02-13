from typing import TypedDict, List, Annotated
import operator
import os
import time
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

from langchain_openai import ChatOpenAI

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

def keep_first_timestamp(left: float, right: float) -> float:
    """Reducer that keeps the first (earliest) timestamp"""
    return left if left else right

class GraphState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    tool_calls: Annotated[int, operator.add] # count tool requests
    retries: Annotated[int, operator.add] # count transient errors
    started_at: Annotated[float, keep_first_timestamp] # timestamp when conversation started

MAX_TOOL_CALLS = 5
TIME_LIMIT_SECONDS = 30  # T seconds time limit
MAX_RETRIES = 3  # Maximum number of retries for failed operations

# ----- Tools
@tool
def add(a: float, b: float) -> float:
    """Return a + b."""
    return float(a) + float(b)

@tool
def multiply(a: float, b: float) -> float:
    """Return a * b."""
    return float(a) * float(b)

@tool
def divide(a: float, b: float) -> float:
    """Return a / b."""
    return float(a) / float(b)

@tool
def count_characters(sentence: str) -> int:
    """<return the length of the string"""
    return len(sentence)

TOOLS = [add, multiply, divide, count_characters]
# ----- LLM bound to tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(TOOLS)


def agent(state: GraphState) -> GraphState:
    max_attempts = MAX_RETRIES + 1
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            resp = llm.invoke(state["messages"]) # AIMessage (may include tool_calls)
            # Increment tool_calls counter by the actual number of tool calls made
            tool_calls = getattr(resp, "tool_calls", None)
            inc = len(tool_calls) if tool_calls else 0
            retry_inc = attempt  # Add retry count to state
            return {"messages": [resp], "tool_calls": inc, "retries": retry_inc}
        
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:  # Don't sleep on the last attempt
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"LLM invoke failed (attempt {attempt + 1}/{max_attempts}), retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)
            else:
                print(f"LLM invoke failed after {max_attempts} attempts: {str(e)}")
    
    # If all attempts failed, return error message
    error_msg = AIMessage(content=f"Sorry, I encountered an error after {max_attempts} attempts: {str(last_exception)}")
    return {"messages": [error_msg], "tool_calls": 0, "retries": max_attempts - 1}

def guard_or_continue(state: GraphState) -> str:
    # Check tool calls limit first
    if state.get("tool_calls", 0) >= MAX_TOOL_CALLS:
        return "exit"
    
    # Check time limit 
    if state.get("started_at", 0) > 0:
        elapsed_time = time.time() - state["started_at"]
        if elapsed_time >= TIME_LIMIT_SECONDS:
            return "time_exit"
    
    # Only if limits are not exceeded, check if tools should be called
    return tools_condition(state)  # "tools" or "__end__"

# ----- Build the graph
graph = StateGraph(GraphState)

# Add nodes
graph.add_node("agent", agent)

# Tool execution node
graph.add_node("tools", ToolNode(TOOLS))

def guard_or_continue(state: GraphState) -> str:
    # Exit when cap reached
    if state.get("tool_calls", 0) >= MAX_TOOL_CALLS:
        return "go to exit"
    # Otherwise follow tools_condition; normalize end labels
    label = tools_condition(state)  # "tools" or END / "__end__"
    if label is END or label == "__end__":
        return "__end__"
    return label

def create_exit_response(state: GraphState, reason: str) -> dict:
    """Create proper response for exit scenarios, handling any pending tool calls"""
    new_messages = []
    
    # Get the last message to check for pending tool calls
    last_message = state["messages"][-1] if state["messages"] else None
    
    # If there are pending tool calls, respond to them first
    if last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            # Create a ToolMessage response indicating the operation was stopped
            tool_response = ToolMessage(
                content=f"{reason} - Operation stopped before completion.",
                tool_call_id=tool_call['id']
            )
            new_messages.append(tool_response)
    
    # Then add the final AI message explaining what happened
    final_message = AIMessage(content=f"{reason} Stopping safely.")
    new_messages.append(final_message)
    
    return {"messages": new_messages}

# Node when max iter tools reached
# graph.add_node("exit", lambda s: create_exit_response(s, "Loop cap reached."))
graph.add_node("exit", END)

# Node when time limit reached  
graph.add_node("time_exit", lambda s: create_exit_response(s, "Time limit reached."))

# Edges
graph.add_edge(START, "agent")

# If the model requested a tool, route to ToolNode; otherwise END
graph.add_conditional_edges("agent", guard_or_continue, {"tools": "tools", "__end__": END, "exit": "exit", "time_exit": "time_exit"})

#Go from tools to Agent again
graph.add_edge("tools", "agent")

memory = MemorySaver()

app = graph.compile(checkpointer=memory)

if __name__ == "__main__":
    
    print("Chat started! Type 'quit' or 'exit' to end the conversation.")
    print("-" * 50)
    
    while True:
        # Get user input
        user_input = input("\nEnter your name to login: ").strip()
        
        # Check for quit conditions
        if user_input.lower() in ['quit', 'exit']:
            print("---------Goodbye!-----------\n")
            break
        
        if not user_input:
            continue

        #Use user name to create thread_id
        thread_id = hash(user_input)
        config = { 'configurable': { 'thread_id': thread_id} }
        
        while True:
            user_input = input("\nEnter your query, logout to change user: ").strip()

            if user_input.lower() == 'logout': break

            # Add user message and get agent response
            # The add_messages reducer will automatically accumulate all messages
            state: GraphState = {
                "messages": [HumanMessage(content=user_input)],
                "tool_calls": 0,
                "retries": 0,
                "started_at": time.time(),  # Set timestamp when conversation starts
            }

            # Streaming run (inspect steps)
            print("\nSTREAM:")
            final = None
            for step_result in app.stream(state, config=config, stream_mode="values"):
                final = step_result  # Keep track of the final result
                # Each step shows the state changes produced by each graph node
                message = step_result['messages'][-1]
                if message.type == "ai" and hasattr(message, 'tool_calls') and message.tool_calls:
                    print(f"Step ({message.type}): Tool calls made:")
                    for tool_call in message.tool_calls:
                        print(f"  - {tool_call['name']}: {tool_call['args']}")
                else:
                    print(f"Step ({message.type}): {message.content}")
            
            if final:
                print("FINAL:\n", final["messages"][-1].content)
                
                # Get final state to access tool_calls count
                final_state = app.get_state(config=config)
                
                # Summary
                print(f"\n--- EXECUTION SUMMARY ---")
                print(f"Total tool calls: {final.get('tool_calls', 0)}")
