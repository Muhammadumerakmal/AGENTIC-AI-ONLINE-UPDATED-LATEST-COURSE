from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
)


def main() -> None:
    result = Runner.run_sync(agent, "Say hello and tell me one fun fact about AI agents.")
    print(result.final_output)


if __name__ == "__main__":
    main()
