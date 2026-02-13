from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from bizlaunch.agents.supervisor import SupervisorAgent
from bizlaunch.agents.ask_clarify_agent import AskClarifyAgent
from bizlaunch.agents.location_agent import LocationAgent
from bizlaunch.agents.market_agent import MarketAgent
from bizlaunch.agents.legal_agent import LegalAgent
from bizlaunch.agents.report_agent import ReportAgent
from bizlaunch.state import AgentState


class BizLaunchGraph:
    def __init__(
        self,
        llm: ChatOpenAI,
        location_tools: list,
        market_tools: list,
        rag_tool,
    ):
        self.llm = llm
        self.supervisor = SupervisorAgent(llm)
        self.ask_clarify_agent = AskClarifyAgent(llm)
        self.location_agent = LocationAgent(llm, location_tools)
        self.market_agent = MarketAgent(llm, market_tools)
        self.legal_agent = LegalAgent(llm, rag_tool)
        self.report_agent = ReportAgent(llm)

        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Add all nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("ask_clarify", self._ask_clarify_node)
        workflow.add_node("location", self._location_node)
        workflow.add_node("market", self._market_node)
        workflow.add_node("legal", self._legal_node)
        workflow.add_node("report", self._report_node)

        # Set supervisor as entry point
        workflow.set_entry_point("supervisor")

        # Supervisor routes to all possible agents
        workflow.add_conditional_edges(
            "supervisor",
            self.supervisor.route,
            {
                "ask_clarify": "ask_clarify",
                "location": "location",
                "market": "market",
                "legal": "legal",
                "report": "report",
                "end": END,
            },
        )

        # After each agent executes, return to supervisor for next decision
        workflow.add_edge("ask_clarify", "supervisor")
        workflow.add_edge("location", "supervisor")
        workflow.add_edge("market", "supervisor")
        workflow.add_edge("legal", "supervisor")

        # Report is final, ends the workflow
        workflow.add_edge("report", END)

        return workflow.compile(checkpointer=self.checkpointer)

    def _supervisor_node(self, state: AgentState) -> dict:
        """Supervisor node that coordinates the workflow and tracks iterations."""
        # Check iteration limit
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return {
                "current_agent": "supervisor",
                "iteration": 1,
                "errors": ["Maximum iterations reached"],
                "final_report": "Maximum iterations reached. The workflow has been terminated. Please restart with a clearer or simpler query.",
            }

        # Supervisor just increments iteration and lets route() decide next step
        return {
            "current_agent": "supervisor",
            "iteration": 1,
        }

    def _ask_clarify_node(self, state: AgentState) -> dict:
        """Node that delegates to AskClarifyAgent."""
        # Check iteration limit
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return {
                "current_agent": "ask_clarify",
                "iteration": 1,
                "errors": ["Maximum iterations reached"],
                "final_report": "Maximum iterations reached. Please restart with a clearer query.",
            }

        result = self.ask_clarify_agent.run(state)
        return {
            **result,
            "current_agent": "ask_clarify",
            "iteration": 1,
        }

    def _location_node(self, state: AgentState) -> dict:
        # Check iteration limit
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return {
                "current_agent": "location",
                "iteration": 1,
                "errors": ["Maximum iterations reached in location agent"],
            }

        result = self.location_agent.run(state)
        return {
            "location_analysis": result["location_analysis"],
            "current_agent": "location",
            "completed_agents": {"location"},
            "iteration": 1,
        }

    def _market_node(self, state: AgentState) -> dict:
        # Check iteration limit
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return {
                "current_agent": "market",
                "iteration": 1,
                "errors": ["Maximum iterations reached in market agent"],
            }

        result = self.market_agent.run(state)
        return {
            "market_analysis": result["market_analysis"],
            "current_agent": "market",
            "completed_agents": {"market"},
            "iteration": 1,
        }

    def _legal_node(self, state: AgentState) -> dict:
        # Check iteration limit
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return {
                "current_agent": "legal",
                "iteration": 1,
                "errors": ["Maximum iterations reached in legal agent"],
            }

        result = self.legal_agent.run(state)
        return {
            "legal_analysis": result["legal_analysis"],
            "current_agent": "legal",
            "completed_agents": {"legal"},
            "iteration": 1,
        }

    def _report_node(self, state: AgentState) -> dict:
        # Check iteration limit
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return {
                "current_agent": "report",
                "iteration": 1,
                "errors": ["Maximum iterations reached in report agent"],
                "final_report": "Unable to complete report due to iteration limit.",
            }

        result = self.report_agent.run(state)
        return {
            "final_report": result["final_report"],
            "current_agent": "report",
            "completed_agents": {"report"},
            "iteration": 1,
        }

    def run(self, user_input: str, thread_id: str, max_iterations: int = 20) -> dict:
        """Executes the workflow with a thread_id for persistence."""
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "input": user_input,
            "messages": [],
            "current_agent": None,
            "completed_agents": set(),
            "iteration": 0,
            "max_iterations": max_iterations,
            "tool_calls": 0,
            "retries": 0,
            "scratch": {},
            "errors": [],
            "location_analysis": None,
            "market_analysis": None,
            "legal_analysis": None,
            "final_report": None,
            "clarification_needed": None,
        }

        result = self.graph.invoke(initial_state, config)
        return result
