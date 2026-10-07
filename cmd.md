# Commands Used

All commands were run from the project root (`class-1/`) in order.

## 1. Check tools were available

```
uv --version
python --version
git --version
```

## 2. Create the project with uv

```
uv init --no-workspace .
```

This scaffolded `pyproject.toml`, `main.py`, `.python-version`, `.gitignore`, and initialized a git repo.

## 3. Install dependencies

```
uv add openai-agents python-dotenv
```

- `openai-agents` — the Agents SDK itself.
- `python-dotenv` — loads the `.env` file so `OPENAI_API_KEY` is available at runtime.

## 4. Run the agent

```
uv run main.py
```

`uv run` creates/uses the project's virtual environment automatically and executes `main.py`.

## 5. Git — first commit

```
git checkout -b setup-gemini-agent
git add .gitignore .python-version README.md main.py pyproject.toml uv.lock
git commit -m "Set up OpenAI Agents SDK project with a working single agent"
```

(`.env` was never staged — it's listed in `.gitignore`.)

## 6. Connect to GitHub and push

```
git ls-remote https://github.com/Muhammadumerakmal/AGENTIC-AI-ONLINE-UPDATED-LATEST-COURSE.git
git remote add origin https://github.com/Muhammadumerakmal/AGENTIC-AI-ONLINE-UPDATED-LATEST-COURSE.git
git branch -M main
git push -u origin main
```

`git ls-remote` was run first just to confirm the remote repo existed and was empty before pushing into it.

## 7. Later updates (README name, MODEL_CHOICE.md, swarm.md)

```
git add <files>
git commit -m "<message>"
git push origin main
```

Same add/commit/push cycle was repeated for each follow-up file.
