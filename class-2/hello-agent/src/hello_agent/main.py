from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()


def main() -> None:
    assistant = Agent(
        name="Assistant",
        instructions="You are a helpful assistant",  # system prompt for the agent.
    )
    result = Runner.run_sync(
        assistant,
        "Write a poem of umer akmal.",
    )
    print(result.final_output)
