from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import State
from src.nodes.planner import PlannerNode
from src.nodes.executor import ExecutorNode
from src.nodes.advance_cursor import AdvanceCursorNode
from src.nodes.retry import RetryNode
from src.nodes.replan import ReplanNode
from src.nodes.finalizer import FinalizerNode

# Configuration
MAX_RETRIES = 2

# Initialize nodes
planner_node = PlannerNode()
executor_node = ExecutorNode()
advance_cursor_node = AdvanceCursorNode()
retry_node = RetryNode()
replan_node = ReplanNode()
finalizer_node = FinalizerNode()

# Build the state graph
builder = StateGraph(State)

# Add all nodes
builder.add_node("planner", planner_node)
builder.add_node("executor", executor_node)
builder.add_node("advance_cursor", advance_cursor_node)
builder.add_node("retry", retry_node)
builder.add_node("replan", replan_node)
builder.add_node("finalize", finalizer_node)

# Set entry point
builder.add_edge(START, "planner")
builder.add_edge("planner", "executor")

def after_executor(state: State):
    """Determine next step after executor runs."""
    plan = state.get("plan")
    steps = plan.steps if plan else []
    i = state.get("step_idx", 0)
    success = state.get("step_success", False)
    retries = state.get("retries", 0)

    if success:
        # Check if there are more steps
        if i + 1 < len(steps):
            return "advance_cursor"
        return "finalize"

    # Failure path
    if retries < MAX_RETRIES:
        return "retry"
    return "replan"

# Add conditional edges from executor
builder.add_conditional_edges("executor", after_executor, {
    "advance_cursor": "advance_cursor",
    "finalize": "finalize",
    "retry": "retry",
    "replan": "replan",
})

# Add loop edges
builder.add_edge("advance_cursor", "executor")
builder.add_edge("retry", "executor")
builder.add_edge("replan", "executor")
builder.add_edge("finalize", END)

# Compile with checkpointer
checkpointer = MemorySaver()
app = builder.compile(checkpointer=checkpointer)