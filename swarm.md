# Swarm, the Agents SDK, and Anthropic's Agent Design Patterns

## 1. What is Swarm?

**Technical:** Swarm was OpenAI's experimental, lightweight framework for orchestrating multi-agent systems. It exposed two core abstractions:

- **Agents** — an entity defined by a system prompt (`instructions`), a set of callable `tools` (functions), and a model.
- **Handoffs** — a special kind of function return value that tells the runtime "stop executing this agent, and transfer control (plus the running conversation context) to a different agent."

The entire framework was intentionally minimal — stateless between calls, no built-in persistence, no production guarantees. It was meant as a reference pattern for how multi-agent coordination *could* work, not something to deploy as-is.

**ELI5:** Imagine a group project where each kid has one job (one kid draws, one kid writes, one kid colors). Swarm is the rulebook that says "if your part is done and it's actually someone else's turn, just hand the paper to them." It's a simple, stripped-down toy version of teamwork — good for learning the idea, not built to survive a real classroom.

## 2. What is the Agents SDK?

**Technical:** The Agents SDK is OpenAI's production-ready successor to Swarm. It keeps the same two core ideas — **Agents** and **handoffs** — but adds the scaffolding needed for real applications:

- A `Runner` that manages the execution loop (including async execution, retries, and streaming).
- **Guardrails** — validation/evaluation hooks that can inspect input or output and halt/redirect execution.
- **Tracing** built in, for debugging and observability.
- First-class support for structured outputs, sessions/memory, and pluggable model providers (not just OpenAI's own models — this is exactly how we pointed it at Gemini earlier via an OpenAI-compatible endpoint).

**ELI5:** If Swarm was the rough draft rulebook sketched on a napkin, the Agents SDK is the official rulebook with a referee (`Runner`), a rulebook checker (guardrails), and a camera recording the game (tracing) — same core game, but now sturdy enough to actually play for real.

## 3. How are they related?

The Agents SDK is a direct evolution of Swarm: same two foundational abstractions (Agents + handoffs), but hardened, documented, and extended for production use. Learning Swarm's model teaches you the Agents SDK's mental model almost for free.

---

## 4. Anthropic's Agent Design Patterns, mapped to the Agents SDK

Anthropic's ["Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents) describes common patterns for composing LLM calls into reliable systems. The Agents SDK gives you concrete primitives for each one.

### Prompt Chaining (Chain Workflow)

**Technical:** Decompose a task into an ordered sequence of LLM calls, where each step's output feeds the next step's input. In the Agents SDK, this is just calling `Runner.run` (or `run_sync`) sequentially, agent after agent, passing each result forward — optionally with a guardrail between steps to validate before continuing.

**ELI5:** Like an assembly line — station 1 cuts the fabric, station 2 sews it, station 3 adds buttons. Each worker only does their one step, then passes it down the line.

### Routing

**Technical:** Classify an incoming request and dispatch it to the agent best suited to handle it. The Agents SDK implements this natively via **handoffs** — an agent can be given a list of other agents it's allowed to hand off to, and the model itself decides (based on the conversation) which one to invoke.

**ELI5:** Like calling a help desk and the first person you talk to says "oh, that's a billing question" and transfers your call to the billing department — without you having to explain everything twice.

### Parallelization

**Technical:** Run multiple independent subtasks concurrently rather than sequentially, then aggregate the results. Since the Agents SDK's `Runner` is built on `async`/`await`, you can launch several agent runs concurrently (e.g., with `asyncio.gather`) and combine their outputs once all finish.

**ELI5:** Instead of one chef cooking the appetizer, then the main course, then dessert one at a time, you have three chefs each cooking one course *at the same time*, so dinner comes out faster.

### Orchestrator–Workers

**Technical:** A top-level "orchestrator" agent breaks a complex goal into subtasks and delegates each to specialized "worker" agents, then assembles their outputs into a final result. In the Agents SDK, this is modeled by giving the orchestrator agent handoffs (or tool-wrapped sub-agents) to each worker, with the orchestrator responsible for sequencing and synthesis.

**ELI5:** Like a project manager who doesn't do the coding, design, or testing themselves — they just figure out who should do what, send out the assignments, and stitch everyone's work together at the end.

### Evaluator–Optimizer

**Technical:** One agent (or LLM call) produces a candidate output; a second "evaluator" assesses it against criteria and feeds back corrections, repeating until the output passes. The Agents SDK supports this via **guardrails** (input/output validation hooks that can reject or flag a response) combined with a loop that re-runs the generator agent until the guardrail passes.

**ELI5:** Like handing your essay to a strict teacher who hands it back with "fix this paragraph" notes, and you keep revising until they finally say "good, that'll do."

---

## Summary

| Concept | Swarm | Agents SDK |
|---|---|---|
| Core abstractions | Agents, handoffs | Agents, handoffs (same idea, hardened) |
| Status | Experimental / educational | Production-ready |
| Extras | — | Runner, guardrails, tracing, sessions, pluggable model providers |
| Anthropic patterns supported | Conceptually, via handoffs | Explicitly, via handoffs + guardrails + async `Runner` |
