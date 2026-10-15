import os

from dotenv import load_dotenv
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from agents.run import RunConfig

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)

gemini = OpenAIChatCompletionsModel(
    model="gemini-3.8-flash",
    openai_client=client,
)


def agent_level() -> None:
    agent = Agent(
        name="AgentLevel",
        instructions="You are a helpful assistant.",
        model=gemini,
    )
    result = Runner.run_sync(agent, "Say hello from agent-level config.")
    print("agent-level:", result.final_output)


def run_level() -> None:
    config = RunConfig(model=gemini)
    agent = Agent(
        name="RunLevel",
        instructions="You are a helpful assistant.",
    )
    result = Runner.run_sync(
        agent,
        "Say hello from run-level config.",
        run_config=config,
    )
    print("run-level:", result.final_output)


def global_level() -> None:
    set_default_openai_api("chat_completions")
    set_default_openai_client(client)
    agent = Agent(
        name="GlobalLevel",
        instructions="You are a helpful assistant.",
    )
    result = Runner.run_sync(agent, "Say hello from global-level config.")
    print("global-level:", result.final_output)


if __name__ == "__main__":
    agent_level()
    run_level()
    global_level()
