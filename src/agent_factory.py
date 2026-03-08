from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

def create_agent(llm, config):
    prompt = ChatPromptTemplate.from_messages(
        [
        (
        "system",
        f"""Role: {config['role']}
        Goal: {config['goal']}
        Backstory: {config['backstory']}

        Rules:
        1. When a tool returns values, always reuse them exactly.
        2. If download_audio returns audio_path, pass that exact path to transcribe_audio.
        3. Never invent placeholders like 'path_to_downloaded_audio_file'.
        4. Only use values returned by tools."""
        ),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
        ]
)

    agent = create_tool_calling_agent(llm, config["allowed_tools"], prompt)

    return AgentExecutor(
        agent=agent,
        tools=config["allowed_tools"],
        verbose=True,
        max_iterations=10,
        return_intermediate_steps=True,
    )