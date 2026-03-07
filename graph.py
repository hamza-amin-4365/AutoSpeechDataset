"""LangGraph agentic pipeline with RAG"""

from typing import TypedDict, Annotated
from pathlib import Path
import tools

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv

load_dotenv()
class PipelineState(TypedDict):
    youtube_url: str
    video_id: str
    audio_path: str
    transcript_path: str
    dataset_path: str
    error: str
    messages: Annotated[list, "messages"]

def init_rag():
    if Path("prd_vectorstore").exists():
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return FAISS.load_local("prd_vectorstore", embeddings, allow_dangerous_deserialization=True)
    
    print("📖 Reading PRD.md and building vector store...")
    if not Path("PRD.md").exists():
        raise FileNotFoundError("PRD.md not found in the current directory.")

    loader = TextLoader("PRD.md")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("prd_vectorstore")
    return vectorstore

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def download_node(state: PipelineState) -> PipelineState:
    print(f"🔗 Checking/Downloading: {state['youtube_url']}")
    try:
        result = tools.download_audio(state["youtube_url"])
        state["video_id"] = result["video_id"]
        state["audio_path"] = result["audio_path"]
        state["messages"].append(f"✓ Audio ready: {result['video_id']}")
    except Exception as e:
        state["error"] = f"Download failed: {str(e)}"
    return state

def transcribe_node(state: PipelineState) -> PipelineState:
    if state.get("error"): return state
    print(f"🎙️ Transcribing audio: {state['audio_path']}")
    try:
        result = tools.transcribe_audio(state["audio_path"])
        state["transcript_path"] = result["transcript_path"]
        state["messages"].append(f"✓ Transcribed: {len(result['segments'])} segments")
    except Exception as e:
        state["error"] = f"Transcription failed: {str(e)}"
    return state

def build_dataset_node(state: PipelineState) -> PipelineState:
    if state.get("error"): return state
    print(f"📊 Building dataset from: {state['transcript_path']}")
    try:
        result = tools.build_dataset(state["transcript_path"], state["audio_path"])
        state["dataset_path"] = result["dataset_path"]
        state["messages"].append(f"✓ Dataset: {result['count']} samples")
    except Exception as e:
        state["error"] = f"Dataset build failed: {str(e)}"
    return state

def rag_advisor_node(state: PipelineState) -> PipelineState:
    if state.get("error"): return state
    print("🧠 Consulting RAG for quality tips...")
    try:
        vectorstore = init_rag()
        query = "Quality guidelines for speech dataset audio length and text accuracy"
        docs = vectorstore.similarity_search(query, k=2)
        context = "\n".join([d.page_content for d in docs])
        
        response = llm.invoke(f"Context: {context}\n\nProvide 1 short quality tip for this pipeline stage.")
        state["messages"].append(f"💡 Tip: {response.content[:1000]}")
    except Exception as e:
        state["messages"].append(f"⚠️ Advisor unavailable: {str(e)}")
    return state

workflow = StateGraph(PipelineState)
workflow.add_node("download", download_node)
workflow.add_node("transcribe", transcribe_node)
workflow.add_node("build", build_dataset_node)
workflow.add_node("advisor", rag_advisor_node)

workflow.set_entry_point("download")
workflow.add_edge("download", "transcribe")
workflow.add_edge("transcribe", "build")
workflow.add_edge("build", "advisor")
workflow.add_edge("advisor", END)

app = workflow.compile()

def run_pipeline(youtube_url: str):
    initial_state = {
        "youtube_url": youtube_url,
        "video_id": "", "audio_path": "", "transcript_path": "",
        "dataset_path": "", "error": "", "messages": []
    }
    result = app.invoke(initial_state)
    print("\n=== Pipeline Summary ===")
    for msg in result["messages"]: print(msg)
    if result.get("error"): print(f"\n❌ Error: {result['error']}")
    else: print(f"\n✅ Final Dataset: {result['dataset_path']}")
    return result