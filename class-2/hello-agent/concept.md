# Class 2 Concepts — OpenAI Agents SDK + uv

What we built and learned, in the order it happened.

---

## 1. Project structure: why `uv` said "Expected a Python module at `src\hello_agent\__init__.py`"

`uv run` does two things: it first **builds/installs your own project**, then runs your command.

Our `pyproject.toml` declares `uv_build` as the build backend:

```toml
[build-system]
requires = ["uv_build>=0.12.3,<0.13.0"]
build-backend = "uv_build"

[project.scripts]
hello-agent = "hello_agent:main"
```

`uv_build` expects a **src layout** — the package lives under `src/`, not at the project root:

```
hello-agent/
├── main.py                  # thin wrapper (optional convenience)
├── pyproject.toml
└── src/
    └── hello_agent/         # package name: hyphens → underscores
        ├── __init__.py
        └── main.py
```

The error happened because `src/hello_agent/__init__.py` didn't exist. Two more clues it was once set up and got lost:

- `.venv\Lib\site-packages\hello_agent.pth` contained `src` — an editable install pointing at a folder that no longer existed
- `[project.scripts] hello-agent = "hello_agent:main"` expects a `hello_agent` module with a `main()` function

**Rule:** project name `hello-agent` → import name `hello_agent` → directory `src/hello_agent/`.

---

## 2. Hello Agent: the two core objects

```python
from agents import Agent, Runner

assistant = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)

result = Runner.run_sync(
    assistant,
    "Write a haiku about recursion in programming.",
)
print(result.final_output)
```

- **`Agent`** = a job description: a system prompt (`instructions`), a name, and optionally tools and a model. It does not talk to any API by itself.
- **`Runner`** = the engine. It takes an agent + an input, calls the model in a loop (handling tool calls, handoffs, guardrails), and returns a `RunResult`. `result.final_output` is the final text.

The SDK's default provider is **OpenAI** — if you don't configure anything, it uses `OPENAI_API_KEY` and an OpenAI model.

---

## 3. Swapping providers: Gemini via the OpenAI-compatible endpoint

Many providers (Gemini, Groq, Together, Ollama, vLLM...) expose an endpoint that **mimics OpenAI's chat-completions API**. The SDK leans on that: you only change *where the HTTP request goes*, not the code that builds it.

```python
import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)  # tracing dashboard expects an OpenAI key

assistant = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model=OpenAIChatCompletionsModel(
        model="gemini-3.8-flash",
        openai_client=client,
    ),
)
```

Three pieces, in order:

1. **`AsyncOpenAI(api_key=..., base_url=...)`** — the OpenAI SDK's HTTP client. It POSTs to `{base_url}/chat/completions` with `Authorization: Bearer <key>`. Pointing `base_url` at Gemini reroutes the exact same request code to Google's servers. The key is Gemini's, not OpenAI's.
2. **`OpenAIChatCompletionsModel(model=..., openai_client=...)`** — an *adapter*. It implements the SDK's Model interface: converts the SDK's internal request into `chat.completions.create(...)` kwargs, sends it through whatever client you hand it, converts the response back. It only needs a model-name string and a client — it doesn't know or care who owns the server.
3. **`Agent(..., model=...)`** — hand the adapter to the agent. If you omit `model`, the SDK fills in its OpenAI default.

`set_tracing_disabled(True)` matters here because OpenAI's tracing dashboard expects an OpenAI key; with a Gemini-only key the traces would fail.

**Note on model names:** we tried `gemini-2.5-flash` (course material) but got a 404 — *"no longer available to new users."* Gemini's error told us to use `gemini-3.8-flash`. Retired model names are common; the error message usually names the replacement.

---

## 4. Why swapping the provider didn't require touching `Agent` or `Runner`

This is the most important design lesson of the class. Three patterns work together:

**Dependency inversion (strategy pattern).**
The SDK defines a `Model` protocol — roughly, "anything with a `get_response(request) -> ModelResponse` method." `Agent` and `Runner` depend only on that protocol, never on a concrete provider. The provider is a *strategy* you plug in.

**Adapter pattern.**
`OpenAIChatCompletionsModel` is an adapter that satisfies the protocol by speaking OpenAI's wire format. Because Gemini exposes an endpoint that mimics that wire format, the *same adapter* works — you only swapped the client's URL and key underneath it.

**Standardized wire format.**
OpenAI's chat-completions JSON shape became a de-facto standard. A "provider swap" is often just: same JSON, different hostname. The model-name string (`"gemini-3.8-flash"`) is passed through opaquely to the server.

**Inversion of control.**
Your code *constructs* the pieces (`client` → `model` → `agent`) and hands them to `Runner`. `Runner` calls back into the objects you gave it; it has no hardcoded knowledge of any of them. So swapping a strategy touches only construction code — the orchestrator is untouched by construction.

```
Runner  ──calls──▶  Agent.model  ──▶  Model protocol
                                          ▲
                    OpenAIChatCompletionsModel implements it
                                          │
                              AsyncOpenAI client (any base_url)
```

One caveat: this adapter path uses chat-completions *semantics*. Gemini-native features (Google's grounding/file APIs, for instance) may need a dedicated model class instead — but for plain chat, the OpenAI-compatible shim is the intended on-ramp.

---

## 5. Model configuration at three scopes

The SDK's default provider is OpenAI; you can override it at three scopes.

### Agent level — override per agent (the course default)

```python
agent = Agent(
    name="Assistant",
    instructions="You only respond in haikus.",
    model=OpenAIChatCompletionsModel(model="gemini-3.8-flash", openai_client=client),
)
```

Different agents in the same app can each have their own `model=` — e.g., a cheap fast model for routing, a stronger model for reasoning.

### Run level — override for one call

```python
from agents.run import RunConfig

config = RunConfig(
    model=OpenAIChatCompletionsModel(model="gemini-3.8-flash", openai_client=client),
)
agent = Agent(name="Assistant", instructions="You are a helpful assistant")
result = Runner.run_sync(agent, "Hello, how are you.", run_config=config)
```

The agent itself is unconfigured; the override applies only to this `Runner.run_sync(...)` call. Useful for A/B testing a model without touching agent definitions.

### Global level — override for the whole process

```python
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled

set_tracing_disabled(True)
set_default_openai_api("chat_completions")
set_default_openai_client(client)
agent = Agent(name="Assistant", instructions="You are a helpful assistant")
```

Every agent created afterward uses this client by default, unless it — or its run — overrides it locally.

### Precedence

The course states: **Agent > Run > Global**.

**Correction from the SDK source:** for models, it's actually **Run > Agent > Global**. `RunConfig.model`'s docstring says *"If set, will override the model set on every agent"* — and our Part-3 experiment proved it: the agent had no model, the run_config supplied Gemini, and Gemini answered. Global is only the fallback when neither specifies one.

Resolution order at run time:

```
run_config.model  →  agent.model  →  SDK default (OpenAI)
```

### When to pick Run-level over Agent-level

| Use Run-level when… | Use Agent-level when… |
|---|---|
| The same agent must run on different models (A/B tests, cost-vs-quality sweeps) | One agent is permanently bound to one model |
| You want a global "run everything on X" switch | Different agents in one workflow need *different* models side by side |
| Per-request model selection (user picks a model in a request) | Model choice is a static property of the agent |

**Rule of thumb:** Agent-level = *what this agent is* (identity). Run-level = *how this execution is configured* (environment). Model is usually identity, so default to Agent-level. Caveat: because RunConfig overrides *every* agent, it's a blunt instrument in multi-agent graphs with handoffs — it flattens per-agent model diversity.

---

## 6. `.env` and secrets

`.env` holds the API keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`). Load it with `load_dotenv()`. Both `.gitignore` files (project + course root) exclude `.env` and `.venv/` — keys never get committed.

---

## Commands we used

```bash
uv run main.py          # build project + run (fixes env automatically)
uv add <package>        # add dependency
git add . && git commit -m "..." && git push
```

## Files in this project

```
hello-agent/
├── .env                          # keys (git-ignored)
├── .gitignore
├── .python-version
├── main.py                       # thin wrapper → calls hello_agent.main()
├── pyproject.toml                # uv_build backend, deps, entry point
├── uv.lock                       # locked dependency versions
└── src/hello_agent/
    ├── __init__.py               # exports main
    └── main.py                   # the actual agent code
```
