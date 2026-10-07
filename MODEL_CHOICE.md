# Why I used OpenAI instead of Gemini

I went with my **OpenAI API key** for this setup instead of Gemini, mainly because I already had a working OpenAI key on hand and wanted to get the agent running without waiting on a new key from Google AI Studio.

That said, I do know how the Gemini version of this setup works conceptually, since Gemini exposes an OpenAI-compatible endpoint:

- Google's Gemini API has an **OpenAI-compatible endpoint** at `https://generativelanguage.googleapis.com/v1beta/openai/`.
- To point the Agents SDK at it, you'd create an `AsyncOpenAI` client with `base_url` set to that endpoint and `api_key=GEMINI_API_KEY` instead of an OpenAI key.
- That client then gets wrapped in an `OpenAIChatCompletionsModel`, passing a Gemini model name (e.g. `gemini-2.0-flash`) along with the client.
- The resulting model object is passed to `Agent(..., model=that_model)`, and `Runner.run` / `Runner.run_sync` work exactly the same from there — the SDK's run loop is `async` under the hood either way, so swapping providers is just a matter of swapping the client/model, not the agent logic itself.

So the only real change between this setup and a Gemini one is the client config (`base_url` + key + model name) — everything else (the `Agent`, `Runner`, instructions, prompt) stays identical.
