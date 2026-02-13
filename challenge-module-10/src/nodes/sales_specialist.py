import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END

from src.state import WorkflowState
from src.config import SALES_SPECIALIST_SYS
from src.tools.sales_tools import SALES_TOOLS
from src.utils.tool_ranker import bind_top_k_tools


def latest_human(messages):
    """Extract the latest human message content."""
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'human':
            return msg.content
    return ""


def sales_agent(state: WorkflowState) -> WorkflowState:
    """Sales agent with dynamic tool binding.

    Implements retrieve -> rank -> bind pattern:
    1. Retrieve: Get all available sales tools
    2. Rank: Score tools by relevance to current task
    3. Bind: Bind only top-K most relevant tools to LLM

    Args:
        state: Current workflow state

    Returns:
        Updated state with sales agent response
    """
    # Get the delegated task or latest human message
    task = state['scratch'].get('specialist_task') or latest_human(state['messages'])
    task_message = HumanMessage(content=task)

    # Only share the delegated task and tool results to keep agent focused
    # Include AIMessages with tool_calls to maintain proper message sequence
    convo = [SystemMessage(content=SALES_SPECIALIST_SYS), task_message]
    for msg in state['messages']:
        # Include AIMessages that have tool_calls and their corresponding ToolMessages
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            convo.append(msg)
        elif isinstance(msg, ToolMessage):
            convo.append(msg)

    # DYNAMIC TOOL BINDING: Retrieve -> Rank -> Bind top-3 tools
    selected_tools, tool_scores = bind_top_k_tools(
        task_description=task,
        all_tools=SALES_TOOLS,
        top_k=3,
        use_embeddings=True
    )

    print(f"\n[Sales Agent] Tool Scores:")
    for tool_name, score in sorted(tool_scores.items(), key=lambda x: x[1], reverse=True):
        indicator = "✓" if tool_name in [t.name for t in selected_tools] else " "
        print(f"  {indicator} {tool_name}: {score:.3f}")

    # Bind selected tools to LLM
    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0,
        api_key=os.getenv('OPENAI_API_KEY')
    ).bind_tools(selected_tools)
    reply = llm.invoke(convo)

    print(f"Sales agent reply: {reply.content}")
    print(f"Sales agent tool calls: {getattr(reply, 'tool_calls', None)}")

    # Let the subgraph handle the full cycle
    return {'messages': [reply]}


def sales_tools_condition(state: WorkflowState) -> str:
    """Check if we should call tools or complete."""
    last_message = state['messages'][-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # Check if any tool requires approval
        tool_names = [tc['name'] for tc in last_message.tool_calls]

        if 'schedule_demo' in tool_names:
            print("[Sales] Demo scheduling requires human approval")
            # For now, we'll call the tool and handle approval in main graph
            # In production, you'd route to approval node here
            return 'tools'

        return 'tools'

    # No tool calls - complete
    return '__end__'


def sales_completion_handler(state: WorkflowState) -> WorkflowState:
    """Mark sales work as complete."""
    return {
        'scratch': {'sales_complete': True},
        'metrics': {'sales_tool_calls': state.get('tool_calls', 0)},
    }


# Build Sales Specialist Subgraph
sales_graph = StateGraph(WorkflowState)
sales_graph.add_node('agent', sales_agent)
sales_graph.add_node('tools', ToolNode(SALES_TOOLS))
sales_graph.add_node('complete', sales_completion_handler)

sales_graph.add_edge(START, 'agent')
sales_graph.add_conditional_edges(
    'agent',
    sales_tools_condition,
    {'tools': 'tools', '__end__': 'complete'}
)
sales_graph.add_edge('tools', 'agent')
sales_graph.add_edge('complete', END)

# Compile the sales subgraph
sales_app = sales_graph.compile()
