"""Main graph construction for CX Support system."""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import WorkflowState
from src.nodes.supervisor import supervisor
from src.nodes.sales_specialist import sales_app
from src.nodes.post_sales_specialist import post_sales_app
from src.nodes.finalizer import finalizer


def create_graph(memory: MemorySaver | None = None):
    """Create the main CX Support workflow graph.

    Graph structure:
        START -> supervisor -> [sales_app/post_sales_app/finalize]

        Each specialist is a compiled subgraph that handles:
        - Agent invocation with dynamic tool binding
        - Tool execution
        - Completion marking

    Args:
        memory: MemorySaver for checkpointing (optional)

    Returns:
        Compiled StateGraph
    """
    # Create main workflow
    builder = StateGraph(WorkflowState)

    # Add nodes (specialists are now compiled subgraphs)
    builder.add_node("supervisor", supervisor)
    builder.add_node("sales_specialist", sales_app)
    builder.add_node("post_sales_specialist", post_sales_app)
    builder.add_node("finalize", finalizer)

    # Set entry point
    builder.add_edge(START, "supervisor")

    # Supervisor routing
    def route_from_supervisor(state: WorkflowState) -> str:
        """Route from supervisor to appropriate specialist or finalizer."""
        stage = state.get('stage') or 'finalize'
        if stage not in {'sales', 'post_sales', 'finalize'}:
            stage = 'finalize'
        return stage

    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "sales": "sales_specialist",
            "post_sales": "post_sales_specialist",
            "finalize": "finalize",
        }
    )

    # Specialists loop back to supervisor when complete
    builder.add_edge("sales_specialist", "supervisor")
    builder.add_edge("post_sales_specialist", "supervisor")

    # Finalizer goes to END
    builder.add_edge("finalize", END)

    # Compile with checkpointing
    if memory:
        return builder.compile(checkpointer=memory)
    else:
        return builder.compile()


def create_graph_with_checkpoints():
    """Create graph with memory checkpointing enabled.

    Returns:
        Compiled graph with checkpointing
    """
    memory = MemorySaver()
    return create_graph(memory=memory)
