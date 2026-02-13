"""Demo script showcasing time-travel and state editing capabilities."""
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.graph.graph import create_graph_with_checkpoints

# Load environment variables from .env file
load_dotenv()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_state_summary(state: dict):
    """Print a summary of the current state."""
    print(f"Stage: {state.get('stage', 'N/A')}")
    print(f"Route: {state.get('route', 'N/A')}")
    print(f"Tool Calls: {state.get('tool_calls', 0)}")
    print(f"Pending Approval: {state.get('pending_approval', False)}")

    scratch = state.get('scratch', {})
    if scratch:
        print(f"Scratch: {list(scratch.keys())}")

    # Show last message
    messages = state.get('messages', [])
    if messages:
        last_msg = messages[-1]
        content = getattr(last_msg, 'content', str(last_msg))
        print(f"Last Message: {content[:100]}...")


def run_normal_flow():
    """Run a normal successful flow with detailed streaming logs."""
    print_section("PART 1: Sales Flow with Streaming - Product Inquiry")

    graph = create_graph_with_checkpoints()
    config = {"configurable": {"thread_id": "demo-sales"}}

    print("📝 Customer Request: 'I'd like to schedule a demo for the Premium Business Laptop'\n")
    print("🔄 Streaming execution steps:\n")

    # Use stream mode for detailed logging
    step_count = 0
    for event in graph.stream(
        {
            "messages": [HumanMessage(content="I'd like to schedule a demo for the Premium Business Laptop")],
            "tool_calls": 0,
            "scratch": {},
            "metrics": {},
        },
        config=config,
        stream_mode="updates"
    ):
        step_count += 1
        for node_name, node_output in event.items():
            print(f"{'─'*70}")
            print(f"Step {step_count}: Node '{node_name}' executed")
            print(f"{'─'*70}")

            # Show key updates
            if 'route' in node_output:
                print(f"  → Routing decision: {node_output['route']}")
            if 'stage' in node_output:
                print(f"  → Current stage: {node_output['stage']}")
            if 'messages' in node_output and node_output['messages']:
                last_msg = node_output['messages'][-1]
                msg_type = type(last_msg).__name__
                content = getattr(last_msg, 'content', '')[:100]
                print(f"  → Message added [{msg_type}]: {content}...")
            if 'scratch' in node_output:
                scratch_keys = list(node_output['scratch'].keys())
                if scratch_keys:
                    print(f"  → Scratch updated: {scratch_keys}")
            print()

    # Get final state
    final_state = graph.get_state(config)

    print(f"\n{'='*70}")
    print("FINAL STATE SUMMARY")
    print(f"{'='*70}")
    print_state_summary(final_state.values)
    print(f"\n✅ Sales flow completed in {step_count} steps")


def run_checkpoint_demo():
    """Demonstrate checkpoint history and state inspection with streaming."""
    print_section("PART 2: Post-Sales Flow with Checkpoints")

    graph = create_graph_with_checkpoints()
    config = {"configurable": {"thread_id": "checkpoint-demo"}}

    # Step 1: Run a workflow with streaming
    print("📝 Customer Request: 'What's the status of order ORD-12345?'\n")
    print("🔄 Streaming execution with tool calls:\n")

    step_count = 0
    for event in graph.stream(
        {
            "messages": [HumanMessage(content="What's the status of order ORD-12345?")],
            "tool_calls": 0,
            "scratch": {},
            "metrics": {},
        },
        config=config,
        stream_mode="updates"
    ):
        step_count += 1
        for node_name, node_output in event.items():
            print(f"{'─'*70}")
            print(f"Step {step_count}: Node '{node_name}' executed")
            print(f"{'─'*70}")

            # Show detailed node outputs
            if 'route' in node_output:
                print(f"  → Routing: {node_output['route']}")
            if 'stage' in node_output:
                print(f"  → Stage: {node_output['stage']}")

            # Show messages with more detail
            if 'messages' in node_output and node_output['messages']:
                for msg in node_output['messages']:
                    msg_type = type(msg).__name__
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"  → AI Message with tool calls:")
                        for tc in msg.tool_calls:
                            print(f"     • {tc['name']}({tc.get('args', {})})")
                    elif msg_type == 'ToolMessage':
                        content = getattr(msg, 'content', '')[:80]
                        print(f"  → Tool Result: {content}...")
                    else:
                        content = getattr(msg, 'content', '')[:80]
                        print(f"  → {msg_type}: {content}...")

            if 'scratch' in node_output:
                scratch_keys = list(node_output['scratch'].keys())
                if scratch_keys:
                    print(f"  → Scratch: {scratch_keys}")
            print()

    # Get final state
    final_state = graph.get_state(config)
    print(f"\n{'='*70}")
    print("FINAL STATE")
    print(f"{'='*70}")
    print_state_summary(final_state.values)
    print(f"\n✅ Post-sales flow completed in {step_count} steps")

    # Step 2: Inspect checkpoints
    print("\n--- Step 2: Checkpoint History ---")
    checkpoints = list(graph.get_state_history(config))
    print(f"📊 Total checkpoints created: {len(checkpoints)}\n")

    for i, checkpoint in enumerate(checkpoints[:6]):
        state_values = checkpoint.values
        stage = state_values.get('stage', 'N/A')
        msg_count = len(state_values.get('messages', []))
        print(f"  Checkpoint {i}: stage={stage:12s} | messages={msg_count}")

    # Step 3: State editing demonstration
    if len(checkpoints) > 2:
        print("\n--- Step 3: State Editing Demo ---")
        checkpoint_state = checkpoints[2].values
        print(f"Selected checkpoint 2 (stage: {checkpoint_state.get('stage')})")

        # Edit state
        edited_state = {
            **checkpoint_state,
            'scratch': {
                **checkpoint_state.get('scratch', {}),
                'demo_edited': True,
                'edit_timestamp': 'checkpoint_2'
            }
        }

        graph.update_state(config, edited_state)
        print("✓ State updated with custom flags in scratch")

        # Verify
        current = graph.get_state(config)
        if current.values.get('scratch', {}).get('demo_edited'):
            print("✓ State edit confirmed")

    print("\n✅ Checkpoint demo complete - checkpointing and state management working!")


def run_complete_demo():
    """Run the complete demonstration."""
    print("\n" + "🎬" * 40)
    print("  CX SUPPORT LANGGRAPH SYSTEM - DEMONSTRATION")
    print("🎬" * 40)

    # Part 1: Normal flow
    run_normal_flow()

    # Part 2: Checkpoint demo
    run_checkpoint_demo()

    print_section("DEMONSTRATION COMPLETE")
    print("""
This demo showcased:

✅ Supervisor routing to Sales and Post-Sales specialists
✅ Dynamic tool binding (retrieve → rank → bind top-3 tools per turn)
✅ Specialist subgraphs with agent → tools → complete flow
✅ Checkpointing with MemorySaver
✅ State inspection and checkpoint history
✅ State editing capabilities

Architecture:
- Main graph: START → supervisor → [sales_specialist/post_sales_specialist] → finalize → END
- Each specialist is a compiled subgraph handling its own tool loop
- Dynamic tool ranking uses embeddings to select top-3 most relevant tools
- GPT-4o-mini model for all LLM calls

Key Files:
- state.py: WorkflowState with reducers
- config.py: All system prompts
- tools/: Sales (7) and Post-Sales (7) mock tools
- utils/tool_ranker.py: Retrieve → Rank → Bind pattern
- nodes/: Supervisor + specialist subgraphs
- graph/graph.py: Main graph compilation
""")


if __name__ == "__main__":
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Please set it to run the demo.")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        exit(1)

    run_complete_demo()
