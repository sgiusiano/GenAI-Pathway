from langchain_core.messages import AIMessage
from src.state import WorkflowState


def finalizer(state: WorkflowState) -> WorkflowState:
    """Finalizer node that wraps up the conversation.

    This node:
    - Summarizes actions taken by specialists
    - Provides final response to customer
    - Marks workflow as complete

    Args:
        state: Current workflow state

    Returns:
        Updated state with final summary
    """
    scratch = state.get('scratch', {})
    metrics = state.get('metrics', {})

    # Build summary of what was accomplished
    summary_parts = []

    sales_done = scratch.get('sales_complete', False)
    post_sales_done = scratch.get('post_sales_complete', False)

    if sales_done:
        summary_parts.append("✓ Sales inquiry handled")

    if post_sales_done:
        summary_parts.append("✓ Support request processed")

    if scratch.get('approval_granted'):
        summary_parts.append("✓ Manager approval obtained")

    if scratch.get('approval_denied'):
        summary_parts.append("✗ Manager approval denied")

    tool_calls_count = state.get('tool_calls', 0)

    if summary_parts:
        summary = "\n".join(summary_parts)
        final_msg = f"""[WORKFLOW COMPLETE]

Actions taken:
{summary}

Total tool calls: {tool_calls_count}

Thank you for contacting support. Is there anything else I can help you with?"""
    else:
        # Simple greeting or acknowledgment
        final_msg = "[Workflow Complete] Thank you for contacting us. How can I assist you today?"

    return {
        'messages': [AIMessage(content=final_msg)],
        'stage': 'complete',
        'metrics': {
            'workflow_complete': True,
            'total_tool_calls': tool_calls_count,
        }
    }
