import asyncio
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

agent = Agent(
    name="Assistant",
    instructions="Answer in one short sentence.",
    model=OpenAIChatCompletionsModel(
        model="gemini-3.8-flash",
        openai_client=client,
    ),
)


async def main() -> None:
    print("--- sequential (await one at a time) ---")
    result = await Runner.run(agent, "What is Python?")
    print(result.final_output)

    print("\n--- concurrent (asyncio.gather) ---")
    results = await asyncio.gather(
        Runner.run(agent, "What is Python?"),
        Runner.run(agent, "What is an AI agent?"),
    )
    for r in results:
        print(r.final_output)


if __name__ == "__main__":
    asyncio.run(main())
