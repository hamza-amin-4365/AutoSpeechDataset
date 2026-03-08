from typing import TypedDict, Annotated, Literal
from pathlib import Path

import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_groq import ChatGroq

from agents_config import EXECUTOR_AGENT_CONFIG, ANALYST_AGENT_CONFIG
from agent_factory import create_agent
from rag import get_rag_advice

class PipelineState(TypedDict):
    youtube_url: str
    video_id: str
    audio_path: str
    transcript_path: str
    transcript_data: dict
    dataset_path: str
    error: str
    messages: Annotated[list, "Internal messages"]
    rag_context: str
    hitl_approved: bool

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

executor_agent = create_agent(llm, EXECUTOR_AGENT_CONFIG)
analyst_agent = create_agent(llm, ANALYST_AGENT_CONFIG)

def executor_node(state: PipelineState):
    result = executor_agent.invoke(
        {"input": f"Download audio for this video: {state['youtube_url']}"}
    )

    audio_path = None
    video_id = None

    for step in result["intermediate_steps"]:
        tool_output = step[1]
        if isinstance(tool_output, dict) and "audio_path" in tool_output:
            audio_path = tool_output["audio_path"]
            video_id = tool_output["video_id"]

    state["audio_path"] = audio_path
    state["video_id"] = video_id

    from tools import transcribe_audio
    transcript = transcribe_audio.invoke({"audio_path": audio_path})

    state["transcript_path"] = transcript["transcript_path"]

    state["messages"].append(f"executor completed {video_id}")

    return state

def analyst_node(state: PipelineState):
    result = analyst_agent.invoke(
        {
            "input": f"Create dataset using transcript {state['transcript_path']} and audio {state['audio_path']}"
        }
    )

    for step in result["intermediate_steps"]:
        tool_output = step[1]
        if isinstance(tool_output, dict) and "dataset_path" in tool_output:
            state["dataset_path"] = tool_output["dataset_path"]

    state["messages"].append("analyst completed")
    return state

def rag_node(state: PipelineState):
    context = get_rag_advice(state)
    state["rag_context"] = context
    state["messages"].append("rag advice generated")
    return state

def approval_node(state: PipelineState):
    print(f"Dataset ready: {state.get('dataset_path')}")
    approval = input("Approve dataset creation? (y/n): ").lower().strip()
    state["hitl_approved"] = approval == "y"
    if not state["hitl_approved"]:
        state["error"] = "approval denied"
    return state

def router(state: PipelineState) -> Literal["rag", "__end__"]:
    if state.get("transcript_path"):
        return "rag"
    return "__end__"

workflow = StateGraph(PipelineState)

workflow.add_node("executor", executor_node)
workflow.add_node("rag", rag_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("approval", approval_node)

workflow.set_entry_point("executor")

workflow.add_conditional_edges(
    "executor",
    router,
    {"rag": "rag", "__end__": END},
)

workflow.add_edge("rag", "analyst")
workflow.add_edge("analyst", "approval")
workflow.add_edge("approval", END)

conn = sqlite3.connect("checkpoint_db.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

app = workflow.compile(checkpointer=memory)

def run_pipeline(youtube_url: str, thread_id: str):
    initial_state = {
        "youtube_url": youtube_url,
        "video_id": "",
        "audio_path": "",
        "transcript_path": "",
        "transcript_data": {},
        "dataset_path": "",
        "error": "",
        "messages": [],
        "rag_context": "",
        "hitl_approved": False,
    }

    config = {"configurable": {"thread_id": thread_id}}

    result = app.invoke(initial_state, config=config)

    print("\nPipeline summary")
    for m in result["messages"]:
        print(m)

    if result.get("error"):
        print("error:", result["error"])
    else:
        print("dataset:", result["dataset_path"])

    return result