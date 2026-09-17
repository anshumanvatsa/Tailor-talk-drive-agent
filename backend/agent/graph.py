from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from agent.nodes import TOOLS, agent_node, should_continue
from agent.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()


drive_agent = build_graph()