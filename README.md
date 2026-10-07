# OpenAI Agents SDK - Class 1

**Name:** Muhammad Ali Akmal

A minimal setup of the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) running a single agent.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you don't have it.
2. Clone this repo and move into it.
3. Create a `.env` file in the project root with your key:
   ```
   OPENAI_API_KEY=your_key_here
   ```
4. Install dependencies:
   ```
   uv sync
   ```

## Run

```
uv run main.py
```

This runs a simple agent that replies to a prompt and prints the response.
