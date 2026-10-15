# Concepts Revision — Runner, asyncio, Model Scopes & Tools (ELI5)

A plain-English revision of Parts 3, 4, and 5. Companion file: `concept.md` (deeper notes).
Runnable examples: `part3_runner_asyncio.py`, `part4_model_config.py`, `part5_tools.py`.

Run any of them from the `hello-agent` folder:

```bash
uv run python part3_runner_asyncio.py
uv run python part4_model_config.py
uv run python part5_tools.py
```

---

## Part 3 — Runner & asyncio

**ELI5:** Ordering pizza by phone. You don't stand frozen at the door while it cooks — you set the table.
Waiting on an LLM is *waiting on the internet* (I/O), not hard thinking (CPU). `asyncio` lets Python do
other work instead of freezing while it waits.

### The three ways to run an agent

| Method | Signature | When to use |
|---|---|---|
| `Runner.run(...)` | `async`, must `await` | Inside `async def` — real apps, servers, concurrent agents |
| `Runner.run_sync(...)` | plain function | Scripts, notebooks, quick tests — builds a loop and blocks for you |
| `Runner.run_streamed(...)` | returns a streaming result | Show tokens/events live instead of waiting for the whole answer |

### The async version, properly

```python
import asyncio
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Answer in one short sentence.")

async def main():
    result = await Runner.run(agent, "Tell me about recursion in programming.")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

- `async def main()` — a **coroutine**: a function that can pause and resume instead of blocking.
- `await Runner.run(...)` — pause `main()` until the LLM replies, without freezing the whole program.
- `asyncio.run(main())` — build the event loop, run `main()` to completion, shut the loop down. The standard entry point.

`run_sync` is a convenience wrapper that drives the same `Runner.run(...)` coroutine on an event loop and blocks.

### Try it: two agents concurrently

```python
results = await asyncio.gather(
    Runner.run(agent, "What is Python?"),
    Runner.run(agent, "What is an AI agent?"),
)
```

Both prompts are in flight at the same time — only possible because `run` is async.

---

## Part 4 — Model configuration at three scopes

**ELI5:** The model is the brain you hire. You can name the brain at three levels — **most specific wins**.

| Level | Where | Analogy |
|---|---|---|
| **Agent level** | `Agent(model=...)` | "This worker uses this brain." |
| **Run level** | `RunConfig(model=...)` | "Just for this one call, use a different brain." |
| **Global level** | `set_default_openai_client(...)` | "Everyone defaults to this brain." |

Course rule: **Agent > Run > Global.**
Correction from the SDK source (proved in Part 3): for models it is actually **Run > Agent > Global** —
`RunConfig.model` overrides the model on *every* agent. Resolution order:

```
run_config.model  →  agent.model  →  SDK default (OpenAI)
```

### 1. Agent level — per agent (course default)

```python
agent = Agent(
    name="Assistant",
    instructions="You only respond in haikus.",
    model=OpenAIChatCompletionsModel(model="gemini-3.8-flash", openai_client=client),
)
```

Different agents can each carry their own `model=` (cheap router vs strong reasoner).

### 2. Run level — for one call

```python
from agents.run import RunConfig

config = RunConfig(model=OpenAIChatCompletionsModel(model="gemini-3.8-flash", openai_client=client))
agent = Agent(name="Assistant", instructions="You are a helpful assistant")
result = Runner.run_sync(agent, "Hello, how are you.", run_config=config)
```

The agent stays unconfigured; the override applies only to this call (good for A/B testing).

### 3. Global level — for the whole process

```python
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled

set_tracing_disabled(True)
set_default_openai_api("chat_completions")
set_default_openai_client(client)
agent = Agent(name="Assistant", instructions="You are a helpful assistant")
```

Every agent created afterward uses this client unless an agent or run overrides it.

**Note:** we use Agent-level in this course so each agent in a multi-agent system can use the model that fits its job.

---

## Part 5 — Tools with `@function_tool`

**ELI5:** Your agent can *talk* but not *do*. A tool is a machine you hand it — like giving a chef a blender.
The chef decides when to press the button.

Write a normal Python function and decorate it:

- **Function name** → tool name
- **Docstring** → tool description (tells the LLM *when* to use it — important!)
- **Type hints** → auto-generated JSON schema for the parameters

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is sunny and 25°C."

agent = Agent(
    name="Weather Assistant",
    instructions="You are a helpful assistant. Use tools when they help you answer.",
    tools=[get_weather],
)
result = Runner.run_sync(agent, "What's the weather like in Karachi?")
print(result.final_output)
```

### What happens on the inside

1. `run_sync` sends your prompt + the tool's schema to the LLM.
2. The LLM answers with "call `get_weather(city='Karachi')`" instead of text.
3. The SDK runs your real Python function with those arguments.
4. The return value is sent back to the LLM as a new message.
5. The LLM writes the final answer. `result.final_output` is ready only after this whole loop.

The agent picks which tools to call on its own, and can chain several in one turn:

```python
@function_tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

agent = Agent(
    name="Assistant",
    instructions="Use tools when they help you answer.",
    tools=[get_weather, add],
)
result = Runner.run_sync(agent, "What's 42 plus 58, and what's the weather in Lahore?")
print(result.final_output)
```

### Beyond `@function_tool`

`@function_tool` is for your own functions. The SDK also ships hosted OpenAI tools (`WebSearchTool`,
`FileSearchTool`) that run on OpenAI's servers. Out of scope here — `@function_tool` is the workhorse you use 90% of the time.
