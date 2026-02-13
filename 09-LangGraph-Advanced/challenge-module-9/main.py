from langchain_core.messages import HumanMessage
from src.graph import app

def print_executor_task(node, retries, config):
    """Show current task for executor node"""
    state = app.get_state(config)
    plan = state.values.get('plan')
    step_idx = state.values.get('step_idx', 0)

    if plan and hasattr(plan, 'steps') and step_idx < len(plan.steps):
        task = plan.steps[step_idx]
        print(f"{node}: step={step_idx}, retries={retries} -> {task.type.value} ({task.description})")
    else:
        print(f"{node}: step={step_idx}, retries={retries}")

def print_event(event, config):
    """Print event information"""
    for node, data in event.items():
        if isinstance(data, dict):
            step = data.get('step_idx', 0)
            retries = data.get('retries', 0)

            if node == "planner" and data.get('plan'):
                # Show plan creation
                plan = data.get('plan')
                print(f"{node}: step={step}, retries={retries}")
                print("  Plan created:")
                for i, plan_step in enumerate(plan.steps):
                    hitl = " [HITL]" if plan_step.requires_interrupt else ""
                    print(f"    {i}: {plan_step.type.value}{hitl}")
            elif node == "executor":
                # Show current task
                print_executor_task(node, retries, config)
            else:
                print(f"{node}: step={step}, retries={retries}")
        else:
            print(f"{node}: executed")

def main(responses=None):
    """
    Run the main execution with predefined responses
    responses: list of 'y' or 'n' responses for interrupts
    """
    if responses is None:
        responses = ['y']  # Default to approve

    response_index = 0
    config = {"configurable": {"thread_id": "1234"}}
    user_input = "What is 2 + 2?"

    print(f"User Input: {user_input}")
    print("\n=== Execution ===")

    # Initial execution
    for event in app.stream({"messages": [HumanMessage(content=user_input)]}, config):
        print_event(event, config)

    # Handle interrupts
    state = app.get_state(config)
    while state.next:
        print(f"\n🛑 INTERRUPTED - Pending: {state.next}")

        # Use predefined response or default to 'y'
        if response_index < len(responses):
            response = responses[response_index].strip().lower()
            response_index += 1
        else:
            response = 'y'  # Default to approve if no more responses

        print(f"Response: {response}")

        if response != 'y':
            print("❌ Stopped by user")
            break

        # Resume execution
        app.update_state(config, {"scratch": {"human_approved": True}})
        for event in app.stream(None, config):
            print_event(event, config)

        state = app.get_state(config)

    print("\n✅ Execution complete")

if __name__ == "__main__":
    main()