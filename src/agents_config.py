from tools import download_audio, transcribe_audio, build_dataset, fetch_youtube_metadata

executor_tools = [download_audio, transcribe_audio, fetch_youtube_metadata]
analyst_tools = [build_dataset]

EXECUTOR_AGENT_CONFIG = {
    "role": "Audio Processing Specialist",
    "backstory": "Expert in retrieving and transcribing audio from URLs.",
    "goal": "Download and transcribe audio.",
    "allowed_tools": executor_tools,
}

ANALYST_AGENT_CONFIG = {
    "role": "Dataset Builder",
    "backstory": "Expert in transforming transcripts into structured datasets.",
    "goal": "Generate a final dataset.",
    "allowed_tools": analyst_tools,
}