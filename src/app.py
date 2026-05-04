"""
Lab 11: Streamlit UI with feedback collection for AutoSpeechDataset.
"""

import uuid
import streamlit as st
from feedback_db import init_db, log_feedback, get_all_feedback

init_db()

st.set_page_config(page_title="AutoSpeechDataset", page_icon="🎙️", layout="wide")
st.title("🎙️ AutoSpeechDataset")
st.caption("Agentic YouTube-to-Speech Dataset Generator")

# Session state init
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"pipeline_{uuid.uuid4().hex[:8]}"
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_feedback" not in st.session_state:
    st.session_state.pending_feedback = None

# Sidebar
with st.sidebar:
    st.header("Session")
    st.code(st.session_state.thread_id, language=None)
    if st.button("New Session"):
        st.session_state.thread_id = f"pipeline_{uuid.uuid4().hex[:8]}"
        st.session_state.history = []
        st.session_state.pending_feedback = None
        st.rerun()

    st.divider()
    st.header("Feedback Log")
    all_fb = get_all_feedback()
    thumbs_up = sum(1 for r in all_fb if r["feedback_score"] == 1)
    thumbs_down = sum(1 for r in all_fb if r["feedback_score"] == -1)
    st.metric("👍 Positive", thumbs_up)
    st.metric("👎 Negative", thumbs_down)

# Chat history display
for entry in st.session_state.history:
    with st.chat_message("user"):
        st.write(entry["user_input"])
    with st.chat_message("assistant"):
        st.write(entry["agent_response"])

# Input
youtube_url = st.chat_input("Paste a YouTube URL to process...")

if youtube_url:
    with st.chat_message("user"):
        st.write(youtube_url)

    with st.chat_message("assistant"):
        with st.spinner("Running pipeline..."):
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                from multi_agent_graph import run_pipeline

                result = run_pipeline(
                    youtube_url=youtube_url,
                    thread_id=st.session_state.thread_id,
                )

                if result.get("error"):
                    response_text = f"❌ Pipeline error: {result['error']}"
                else:
                    lines = [
                        f"✅ Video ID: `{result.get('video_id', 'N/A')}`",
                        f"📄 Transcript: `{result.get('transcript_path', 'N/A')}`",
                        f"📦 Dataset: `{result.get('dataset_path', 'N/A')}`",
                    ]
                    if result.get("messages"):
                        lines.append("\n**Pipeline log:**")
                        lines.extend([f"- {m}" for m in result["messages"]])
                    response_text = "\n".join(lines)

            except Exception as e:
                response_text = f"❌ Error: {str(e)}"

        st.markdown(response_text)

    message_id = uuid.uuid4().hex
    entry = {
        "message_id": message_id,
        "user_input": youtube_url,
        "agent_response": response_text,
    }
    st.session_state.history.append(entry)
    st.session_state.pending_feedback = entry

# Feedback widget for the latest response
if st.session_state.pending_feedback:
    entry = st.session_state.pending_feedback
    st.divider()
    st.write("**Was this response helpful?**")

    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("👍", key="thumbs_up"):
            log_feedback(
                thread_id=st.session_state.thread_id,
                message_id=entry["message_id"],
                user_input=entry["user_input"],
                agent_response=entry["agent_response"],
                feedback_score=1,
            )
            st.session_state.pending_feedback = None
            st.success("Thanks for the feedback!")
            st.rerun()
    with col2:
        if st.button("👎", key="thumbs_down"):
            st.session_state.show_comment = True

    if st.session_state.get("show_comment"):
        comment = st.text_area("What went wrong? (optional)")
        if st.button("Submit feedback"):
            log_feedback(
                thread_id=st.session_state.thread_id,
                message_id=entry["message_id"],
                user_input=entry["user_input"],
                agent_response=entry["agent_response"],
                feedback_score=-1,
                optional_comment=comment,
            )
            st.session_state.pending_feedback = None
            st.session_state.show_comment = False
            st.warning("Feedback recorded. We'll use this to improve.")
            st.rerun()
