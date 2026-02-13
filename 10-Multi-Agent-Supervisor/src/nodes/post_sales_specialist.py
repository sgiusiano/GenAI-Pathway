import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END

from src.state import WorkflowState
from src.config import POST_SALES_SPECIALIST_SYS
from src.tools.post_sales_tools import POST_SALES_TOOLS
from src.utils.tool_ranker import bind_top_k_tools


def latest_human(messages):
    """Extract the latest human message content."""
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'human':
            return msg.content
    return ""


def post_sales_agent(state: WorkflowState) -> WorkflowState:
    """Post-sales agent with dynamic tool binding.

    Implements retrieve -> rank -> bind pattern:
    1. Retrieve: Get all available post-sales tools
    2. Rank: Score tools by relevance to current task
    3. Bind: Bind only top-K most relevant tools to LLM

    Args:
        state: Current workflow state

    Returns:
        Updated state with post-sales agent response
    """
    # Get the delegated task or latest human message
    task = state['scratch'].get('specialist_task') or latest_human(state['messages'])
    task_message = HumanMessage(content=task)

    # Only share the delegated task and tool results to keep agent focused
    # Include AIMessages with tool_calls to maintain proper message sequence
    convo = [SystemMessage(content=POST_SALES_SPECIALIST_SYS), task_message]
    for msg in state['messages']:
        # Include AIMessages that have tool_calls and their corresponding ToolMessages
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            convo.append(msg)
        elif isinstance(msg, ToolMessage):
            convo.append(msg)

    # DYNAMIC TOOL BINDING: Retrieve -> Rank -> Bind top-3 tools
    selected_tools, tool_scores = bind_top_k_tools(
        task_description=task,
        all_tools=POST_SALES_TOOLS,
        top_k=3,
        use_embeddings=True
    )

    print(f"\n[Post-Sales Agent] Tool Scores:")
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

    print(f"Post-sales agent reply: {reply.content}")
    print(f"Post-sales agent tool calls: {getattr(reply, 'tool_calls', None)}")

    # Let the subgraph handle the full cycle
    return {'messages': [reply]}


def post_sales_tools_condition(state: WorkflowState) -> str:
    """Check if we should call tools or complete."""
    last_message = state['messages'][-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # Check if any tool requires approval
        tool_names = [tc['name'] for tc in last_message.tool_calls]

        if 'process_refund' in tool_names:
            print("[Post-Sales] Refund processing requires human approval")
            # For now, we'll call the tool and handle approval in main graph
            # In production, you'd route to approval node here
            return 'tools'

        return 'tools'

    # No tool calls - complete
    return '__end__'


def post_sales_completion_handler(state: WorkflowState) -> WorkflowState:
    """Mark post-sales work as complete."""
    return {
        'scratch': {'post_sales_complete': True},
        'metrics': {'post_sales_tool_calls': state.get('tool_calls', 0)},
    }


# Build Post-Sales Specialist Subgraph
post_sales_graph = StateGraph(WorkflowState)
post_sales_graph.add_node('agent', post_sales_agent)
post_sales_graph.add_node('tools', ToolNode(POST_SALES_TOOLS))
post_sales_graph.add_node('complete', post_sales_completion_handler)

post_sales_graph.add_edge(START, 'agent')
post_sales_graph.add_conditional_edges(
    'agent',
    post_sales_tools_condition,
    {'tools': 'tools', '__end__': 'complete'}
)
post_sales_graph.add_edge('tools', 'agent')
post_sales_graph.add_edge('complete', END)

# Compile the post-sales subgraph
post_sales_app = post_sales_graph.compile()
