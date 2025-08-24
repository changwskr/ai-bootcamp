from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import MessagesState, END
from langgraph.types import Command
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent


members = ["cafeteria", "schedule"]
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal[*options]

class State(MessagesState):
    next: str


def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    if goto == "FINISH":
        goto = END

    return Command(goto=goto, update={"next": goto})


cafeteria_agent = create_react_agent(
    llm, tools=[get_cafeteria_menu], prompt="당신은 구내식당을 관리하는 영양사입니다. 사용자에게 이번 주의 식단을 알려줄 수 있습니다."
)

def cafeteria_node(state: State) -> Command[Literal["supervisor"]]:
    result = cafeteria_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="cafeteria")
            ]
        },
        goto="supervisor",
    )

schedule_agent = create_react_agent(
    llm, tools=[get_schedule], prompt="당신은 사용자의 일정을 관리하는 비서입니다. 사용자에게 현재 남아있는 일정을 안내합니다."
)

def schedule_node(state: State) -> Command[Literal["supervisor"]]:
    result = schedule_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="schedule")
            ]
        },
        goto="supervisor",
    )

builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("cafeteria", cafeteria_node)
builder.add_node("schedule", schedule_node)
graph = builder.compile()

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass