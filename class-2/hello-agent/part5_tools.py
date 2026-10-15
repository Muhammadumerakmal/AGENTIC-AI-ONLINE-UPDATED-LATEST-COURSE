import os

from dotenv import load_dotenv
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)


@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is sunny and 25°C."


@function_tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant. Use tools when they help you answer.",
    tools=[get_weather, add],
    model=OpenAIChatCompletionsModel(
        model="gemini-3.8-flash",
        openai_client=client,
    ),
)


def main() -> None:
    result = Runner.run_sync(
        agent,
        "What's 42 plus 58, and what's the weather in Lahore?",
    )
    print(result.final_output)


if __name__ == "__main__":
    main()
