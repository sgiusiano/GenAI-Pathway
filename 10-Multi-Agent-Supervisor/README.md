# Challenge Module 10 - CX Support LangGraph System

A production-minded LangGraph agent system demonstrating:
- ✅ Supervisor routing to multiple specialist subgraphs
- ✅ Dynamic tool binding (retrieve → rank → bind top-K pattern)
- ✅ Checkpointing and time-travel capabilities
- ✅ Human-in-the-loop approval for side-effect operations
- ✅ State editing and execution forking

## Architecture

### System Overview

```
Customer Request
      ↓
  Supervisor (routes to specialists)
      ↓
  ┌───────────────┬──────────────────┐
  ↓               ↓                  ↓
Sales         Post-Sales        Finalize
Specialist    Specialist
  ↓               ↓
Dynamic Tool  Dynamic Tool
Binding       Binding
  ↓               ↓
7 Sales       7 Support
Tools         Tools
  ↓               ↓
Human         Human
Approval      Approval
(for demos)   (for refunds)
```

### Components

**1. Supervisor** ([supervisor.py](src/nodes/supervisor.py))
- Routes customer requests to appropriate specialists
- Decisions: `sales`, `post_sales`, or `finalize`
- Uses GPT-4o-mini with structured output

**2. Sales Specialist** ([sales_specialist.py](src/nodes/sales_specialist.py))
- Handles pre-purchase inquiries
- Dynamic tool binding: retrieves all 7 tools, ranks by relevance, binds top-3
- Tools:
  - `search_product_catalog`
  - `get_pricing`
  - `check_inventory`
  - `calculate_discount`
  - `schedule_demo` ⚠️ (requires human approval)
  - `get_competitor_comparison`
  - `check_customer_eligibility`

**3. Post-Sales Specialist** ([post_sales_specialist.py](src/nodes/post_sales_specialist.py))
- Handles post-purchase support
- Dynamic tool binding: retrieves all 7 tools, ranks by relevance, binds top-3
- Tools:
  - `search_knowledge_base`
  - `check_order_status`
  - `process_refund` ⚠️ (requires human approval)
  - `escalate_ticket`
  - `update_account_settings`
  - `check_warranty`
  - `get_troubleshooting_steps`

**4. Human Approval** ([human_approval.py](src/nodes/human_approval.py))
- Interrupts execution before side-effect operations
- Simulates manager approval workflow
- Checkpoints state for time-travel

**5. Tool Ranker** ([tool_ranker.py](src/utils/tool_ranker.py))
- Implements retrieve → rank → bind pattern
- Uses OpenAI embeddings for semantic similarity
- Fallback to keyword matching if embeddings fail

## Dynamic Tool Binding

Each specialist uses a **retrieve → rank → bind** pattern:

1. **Retrieve**: Access all 7 available tools
2. **Rank**: Score tools using cosine similarity between task embedding and tool description embeddings
3. **Bind**: Bind only top-3 most relevant tools to LLM

Example output:
```
[Sales Specialist] Tool Scores:
  ✓ get_pricing: 0.856
  ✓ search_product_catalog: 0.823
  ✓ check_inventory: 0.791
    calculate_discount: 0.654
    schedule_demo: 0.432
    get_competitor_comparison: 0.387
    check_customer_eligibility: 0.312
```

## Time-Travel Demo

The system demonstrates **checkpoint-based time-travel**:

### Scenario: Refund Request Repair

1. **Initial Execution**: Customer requests refund → Denied (simulated bad outcome)
2. **Fork Checkpoint**: Load state before approval decision
3. **Edit State**: Set `force_approve_refund = True` in scratch
4. **Resume Execution**: Re-run from checkpoint with edited state
5. **Result**: Refund approved (repaired outcome)

### Code Example

```python
# Edit state at checkpoint
edited_state = {
    **checkpoint_state,
    'scratch': {
        **checkpoint_state.get('scratch', {}),
        'force_approve_refund': True,  # Override denial
    }
}

# Resume from edited checkpoint
graph.update_state(config, edited_state, as_node="human_approval")
result = graph.invoke(None, config=config)
```

## Installation

```bash
# Clone repository
git clone <repository-url>
cd challenge-module-10

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Run Complete Demo

```bash
python -m src.main
```

This runs:
1. Normal flow: Sales demo request (approved)
2. Time-travel demo: Refund denial → state edit → approval

### Custom Usage

```python
from src.graph import create_graph_with_checkpoints
from langchain_core.messages import HumanMessage

# Create graph with checkpointing
graph = create_graph_with_checkpoints("checkpoints.sqlite")

# Run workflow
config = {"configurable": {"thread_id": "customer-123"}}
result = graph.invoke(
    {
        "messages": [HumanMessage(content="I want to buy a laptop")],
        "tool_calls": 0,
        "scratch": {},
        "metrics": {},
    },
    config=config
)

# Access checkpoint history
checkpoints = list(graph.get_state_history(config))
```

## Project Structure

```
challenge-module-10/
├── src/
│   ├── __init__.py
│   ├── config.py              # All system prompts
│   ├── state.py               # State definitions
│   ├── graph.py               # Main graph compilation
│   ├── main.py                # Demo script
│   ├── nodes/
│   │   ├── supervisor.py      # Supervisor routing
│   │   ├── sales_specialist.py
│   │   ├── post_sales_specialist.py
│   │   ├── human_approval.py
│   │   └── finalizer.py
│   ├── tools/
│   │   ├── sales_tools.py     # 7 sales tools
│   │   └── post_sales_tools.py # 7 support tools
│   └── utils/
│       └── tool_ranker.py     # Dynamic tool binding
├── requirements.txt
└── README.md
```

## Key Features

### ✅ Challenge Requirements Met

1. **Supervisor + 2 Specialists**: Supervisor routes to Sales and Post-Sales subgraphs
2. **Dynamic Tool Binding**: Each specialist uses retrieve → rank → bind pattern per turn
3. **Checkpointing**: SqliteSaver stores state at each step
4. **Time-Travel**: Fork execution, edit state, resume from checkpoint
5. **Human Approval**: Interrupt before side-effects (demos, refunds)
6. **Production-Minded**: Structured states, error handling, fallback mechanisms

### Model Configuration

- All LLMs use GPT-4o-mini (`gpt-4o-mini`)
- Temperature: 0 (deterministic)
- Embeddings: `text-embedding-3-small` for tool ranking

### Prompts

All prompts stored in [config.py](src/config.py):
- `SUPERVISOR_SYS`: Supervisor routing instructions
- `SALES_SPECIALIST_SYS`: Sales specialist behavior
- `POST_SALES_SPECIALIST_SYS`: Post-sales specialist behavior

## Example Interactions

### Sales Inquiry
```
User: "I want to buy a laptop. What's available?"
→ Supervisor routes to Sales
→ Sales binds: search_product_catalog, get_pricing, check_inventory
→ Returns product information
→ Finalize
```

### Support Request
```
User: "My order ORD-12345 hasn't arrived. Can I get a refund?"
→ Supervisor routes to Post-Sales
→ Post-Sales binds: check_order_status, check_warranty, process_refund
→ Triggers human approval for refund
→ [Approval node interrupts]
→ After approval: processes refund
→ Finalize
```

## Design Decisions

1. **Minimal but Complete**: Focused on core requirements without unnecessary complexity
2. **Mock Data**: Realistic mock tools simulate production behavior
3. **Semantic Ranking**: Embeddings-based tool selection (with keyword fallback)
4. **Explicit State Management**: Clear state schemas for all components
5. **Checkpointing Strategy**: SQLite for persistence, easy to inspect and debug

## Testing Time-Travel

The [main.py](src/main.py) demo includes:
- Checkpoint creation during execution
- State inspection at each checkpoint
- State editing capabilities
- Execution forking from arbitrary checkpoints
- Outcome repair demonstration

## Future Enhancements

- Real database integration for orders/products
- Actual manager approval notification system
- Multi-turn tool calling optimization
- Streaming responses for better UX
- A/B testing different tool ranking strategies

## License

This is a challenge submission for the GenAI Pathway program.

---

**Author**: Santiago Ariel Giusiano
**Challenge**: Module 10 - Advanced LangGraph Patterns
**Date**: October 2025
