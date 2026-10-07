import os

from dotenv import find_dotenv, load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner

load_dotenv(find_dotenv())

# 1. Point an OpenAI-compatible client at Gemini's endpoint instead of OpenAI's
external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Wrap it as a Chat Completions model the SDK understands
llm_model = OpenAIChatCompletionsModel(
    model="gemini-3.8-flash",
    openai_client=external_client,
)

# 3. Hand that model to the Agent instead of using the default
agent = Agent(name="Assistant", model=llm_model)


def main() -> None:
    result = Runner.run_sync(agent, "Welcome and motivate me to learn Agentic AI.")
    print("AGENT RESPONSE:", result.final_output)


if __name__ == "__main__":
    main()
