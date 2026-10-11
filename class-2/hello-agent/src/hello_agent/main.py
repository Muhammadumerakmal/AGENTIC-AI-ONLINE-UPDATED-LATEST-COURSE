import os

from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner

load_dotenv()

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

gemini_model = OpenAIChatCompletionsModel(
    model="gemini-3.8-flash",
    openai_client=gemini_client,
)

gemini_run_config = RunConfig(model=gemini_model)

assistant = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)


def main() -> None:
    print("=== WITH Gemini run_config ===")
    gemini_result = Runner.run_sync(
        assistant,
        "fifa world cup 2026 winner",
        run_config=gemini_run_config,
    )
    print(gemini_result.final_output)

    print("\n=== WITHOUT run_config (agent default) ===")
    default_result = Runner.run_sync(
        assistant,
        "fifa world cup 2026 winner",
    )
    print(default_result.final_output)


if __name__ == "__main__":
    main()
