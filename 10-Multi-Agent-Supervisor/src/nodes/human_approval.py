from langchain_core.messages import AIMessage
from src.state import WorkflowState


def human_approval(state: WorkflowState) -> WorkflowState:
    """Human-in-the-loop approval node for side-effect operations.

    This node interrupts execution before actions with real-world consequences
    (demo scheduling, refund processing) and waits for human approval.

    In production, this would:
    - Send notification to manager
    - Wait for approval/rejection
    - Resume or cancel based on decision

    For this demo, we simulate the approval process.

    Args:
        state: Current workflow state

    Returns:
        Updated state with approval status
    """
    last_message = state['messages'][-1]

    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        # No tool calls - shouldn't be here
        return {
            'messages': [AIMessage(content="[Approval] No actions requiring approval")],
            'pending_approval': False,
        }

    # Extract tool calls requiring approval
    approval_requests = []
    for tc in last_message.tool_calls:
        tool_name = tc['name']
        tool_args = tc.get('args', {})

        if tool_name == 'schedule_demo':
            approval_requests.append({
                'type': 'Demo Scheduling',
                'details': f"Product: {tool_args.get('product_sku')}, "
                          f"Customer: {tool_args.get('customer_email')}, "
                          f"Date: {tool_args.get('preferred_date')}"
            })
        elif tool_name == 'process_refund':
            approval_requests.append({
                'type': 'Refund Processing',
                'details': f"Order: {tool_args.get('order_id')}, "
                          f"Amount: ${tool_args.get('amount', 0):.2f}, "
                          f"Reason: {tool_args.get('reason')}"
            })

    if not approval_requests:
        return {
            'messages': [AIMessage(content="[Approval] No high-risk actions detected")],
            'pending_approval': False,
        }

    # Format approval request
    approval_summary = "\n".join([
        f"  • {req['type']}: {req['details']}"
        for req in approval_requests
    ])

    approval_msg = f"""[HUMAN APPROVAL REQUIRED]

The following actions require manager approval:

{approval_summary}

⚠️ Execution paused. Awaiting approval decision.

In production, this would:
1. Notify the appropriate manager
2. Create approval ticket in system
3. Wait for approval/rejection
4. Resume execution based on decision

For demo purposes, approval is simulated in the graph execution."""

    print("\n" + "="*70)
    print(approval_msg)
    print("="*70 + "\n")

    return {
        'messages': [AIMessage(content=approval_msg)],
        'pending_approval': True,
        'scratch': {
            'approval_requests': approval_requests,
            'awaiting_human_approval': True,
        }
    }


def check_approval_decision(state: WorkflowState) -> str:
    """Check if approval was granted or denied.

    In a real system, this would check an approval database/queue.
    For demo, we simulate approval based on state flags.

    Args:
        state: Current workflow state

    Returns:
        'approved' or 'denied'
    """
    scratch = state.get('scratch', {})

    # Check for simulated approval override (for time-travel demo)
    if scratch.get('force_approve_refund') or scratch.get('force_approve_demo'):
        print("[Approval] ✓ APPROVED (simulated)")
        return 'approved'

    # Default: Approve demos, deny refunds (to simulate bad outcome for demo)
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tc in last_message.tool_calls:
            if tc['name'] == 'process_refund':
                print("[Approval] ✗ DENIED (simulated - for time-travel demo)")
                return 'denied'
            elif tc['name'] == 'schedule_demo':
                print("[Approval] ✓ APPROVED (simulated)")
                return 'approved'

    return 'approved'


def apply_approval_decision(state: WorkflowState) -> WorkflowState:
    """Apply the approval decision and update state.

    Args:
        state: Current workflow state

    Returns:
        Updated state with approval result
    """
    decision = check_approval_decision(state)

    if decision == 'approved':
        return {
            'messages': [AIMessage(content="[Approval] ✓ Request approved. Proceeding with action.")],
            'pending_approval': False,
            'scratch': {'approval_granted': True},
        }
    else:
        return {
            'messages': [AIMessage(content="[Approval] ✗ Request denied. Action cancelled.")],
            'pending_approval': False,
            'scratch': {
                'approval_granted': False,
                'approval_denied': True,
            },
        }
