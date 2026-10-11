import os

from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner

load_dotenv()

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

gemini_model = OpenAIChatCompletionsModel(
    model="gemini-3.8-flash",
    openai_client=gemini_client,
)


def main() -> None:
    assistant = Agent(
        name="Assistant",
        instructions="You are a helpful assistant",
        model=gemini_model,
    )
    result = Runner.run_sync(
        assistant,
        "Write a haiku about recursion in programming.",
    )
    print(result.final_output)


if __name__ == "__main__":
    main()
