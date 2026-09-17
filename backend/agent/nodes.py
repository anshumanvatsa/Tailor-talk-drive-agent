from config import settings
from agent.prompts import SYSTEM_PROMPT
from agent.state import AgentState
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from tools.drive_list_types import list_drive_summary
from tools.drive_metadata import get_file_details
from tools.drive_search import search_drive_files

TOOLS = [search_drive_files, get_file_details, list_drive_summary]


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.groq_api_key,
        temperature=0.2,
    ).bind_tools(TOOLS)


def agent_node(state: AgentState) -> AgentState:
    llm = get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
    response = llm.invoke(messages)

    tools_used = state.get("tools_used", [])
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            tools_used.append(tc["name"])

    return {"messages": [response], "tools_used": tools_used}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"