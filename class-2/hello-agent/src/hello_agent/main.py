import os

from dotenv import load_dotenv
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)

assistant = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model=OpenAIChatCompletionsModel(
        model="gemini-3.8-flash",
        openai_client=client,
    ),
)


def main() -> None:
    result = Runner.run_sync(
        assistant,
        "fifa world cup 2026 winner",
    )
    print(result.final_output)


if __name__ == "__main__":
    main()
