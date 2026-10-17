# Codex follow-up prompts — the human stays in control

## The FIRST prompt
Use `CODEX_START_HERE.md` exactly. This should run B00 only; no code development beyond audit/tracking initialization.

## After any task is accepted (copy/paste)
> Continue Civicly with **only the next TODO microtask** in `docs/backend/11_microtasks.md` and `task_board.md`. Read `AGENTS.md` and the relevant contracts first. Briefly tell me the files/behavior you will implement, then implement and run its acceptance tests. Update `decision.md`, `flow.md`, `implementation_status.md`, `test_log.md`, `blockers.md`, and `task_board.md`. Show exact terminal commands and results, distinguish mock/spec tests from real FalkorDB/MCP/LLM integration. Provide simple verification steps I can run myself, then **STOP** for my review. Do not begin the following task or any frontend code.

## If an integration fails (copy/paste)
> Do not proceed to another microtask. Reproduce this failure with the smallest executable test. Read official vendor documentation for the installed version. Diagnose root cause without changing Civicly requirements. Record commands/stack trace in `blockers.md`, alternatives and decision in `decision.md`, changes in `flow.md`, failed/passing attempts in `test_log.md`. Propose the smallest correction and exact verification command. Stop after the fix or if human input is needed.

## Before reviewing a Codex task
Run the command it gives you. Check whether it used a real FalkorDB instance, actual MCP `tools/list`/`tools/call`, true persisted graph changes, and a real LLM where that milestone requires one. Ask where to find the trace/fixture IDs. If only unit mocks ran, task cannot be marked integrated.

## When asking ChatGPT for diagnosis
Share these files from the updated repository: `decision.md`, `flow.md`, `implementation_status.md`, `test_log.md`, `blockers.md`, and relevant failing implementation files. Include exact error output and your current microtask ID. No need to paste your entire repo if the issue is localized.

## Before backend → frontend
> Do a backend-only final review against R01–R18 and B-END. Run all actual integration and behavior tests; produce a requirement-to-evidence matrix with paths and test commands. Verify that every frontend-relevant case state, evidence graph, agent trace, plan DAG, approval and outcome has a stable typed API response/event. List remaining gaps and stop. **Do not start frontend until I approve.**

## Codex response report I expect every time
```
Task ID:
Intent and user-visible behavior:
Files changed:
Significant decisions / alternatives:
Actual commands executed:
Tests: pass / fail / skipped (reason):
Where to inspect FalkorDB graph / MCP trace / API response:
My two-minute verification instructions:
Open blockers:
Next single task:
STOP for approval.
```

## Why the logs matter
- `decision.md`: what Codex chose and why, including version/compatibility evidence and trade-offs.
- `flow.md`: what files were created, import dependencies, endpoint/tool/graph data flow, where to debug.
- `test_log.md`: objective proof, not verbal assurance.
- `implementation_status.md`: what's really built and what remains.
- `blockers.md`: errors and reproductions.
- `task_board.md`: stage completion with human verification.
