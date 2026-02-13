import os
from typing import Literal

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage

from src.state import WorkflowState
from src.config import SUPERVISOR_SYS


class SupervisorDecision(BaseModel):
    """Supervisor's routing decision for CX support."""
    decision: Literal['sales', 'post_sales', 'finalize'] = Field(
        ...,
        description='Which specialist to route to next'
    )
    summary: str = Field(
        ...,
        description='Brief explanation for the user about the routing decision'
    )
    specialist_task: str | None = Field(
        default=None,
        description='Specific task guidance for the specialist',
    )


supervisor_llm = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0,
    api_key=os.getenv('OPENAI_API_KEY')
).with_structured_output(SupervisorDecision)


def latest_human(messages: list[BaseMessage]) -> str:
    """Extract the latest human message content."""
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'human':
            return msg.content
    return ""


def supervisor(state: WorkflowState) -> dict:
    """Supervisor node that routes customer requests to appropriate specialists.

    Routes to:
    - 'sales': Pre-purchase inquiries (products, pricing, demos)
    - 'post_sales': Post-purchase support (orders, refunds, issues)
    - 'finalize': When specialists have completed their work
    """
    messages = [SystemMessage(content=SUPERVISOR_SYS)] + state['messages']
    decision = supervisor_llm.invoke(messages)

    scratch_view = state.get('scratch', {})
    user_message = latest_human(state['messages'])

    sales_keywords = ['product', 'price', 'pricing', 'buy', 'purchase', 'demo',
                      'inventory', 'stock', 'discount', 'compare', 'laptop',
                      'headphones', 'monitor', 'keyboard', 'mouse']

    post_sales_keywords = ['order', 'refund', 'return', 'tracking', 'warranty',
                           'support', 'broken', 'not working', 'troubleshoot',
                           'help', 'issue', 'problem', 'account', 'password']

    needs_sales = any(kw in user_message.lower() for kw in sales_keywords)
    needs_post_sales = any(kw in user_message.lower() for kw in post_sales_keywords)

    sales_done = scratch_view.get('sales_complete', False)
    post_sales_done = scratch_view.get('post_sales_complete', False)

    if needs_post_sales and not post_sales_done:
        route = 'post_sales'
    elif needs_sales and not sales_done:
        route = 'sales'
    elif (not needs_sales or sales_done) and (not needs_post_sales or post_sales_done):
        route = 'finalize'
    else:
        route = decision.decision

    if route != decision.decision:
        print(f"[Supervisor] Overriding LLM decision '{decision.decision}' with '{route}'")

    ai_msg = AIMessage(content=f"[Supervisor] {decision.summary}")

    update: dict = {
        'messages': [ai_msg],
        'route': route,
        'stage': route,
        'metrics': {'supervisor_last_route': route},
    }

    if decision.specialist_task:
        update['scratch'] = {'specialist_task': decision.specialist_task}

    return update
