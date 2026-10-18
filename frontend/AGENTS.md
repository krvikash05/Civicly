# Frontend operating scope

The human explicitly authorized parallel frontend/backend work on 2026-10-18. This supersedes the former backend B-END prerequisite for frontend development; it does not waive any backend acceptance, security, provenance or live-provider requirement.

Work only on the next unchecked task in frontend/docs/tasks.md, one microtask per review. Read frontend/README.md and docs/integration.md and current root contracts before coding. Keep app/dependencies/tests inside frontend/. Do not edit backend code, contracts, runtime configuration, datasets or shared database state as a frontend task. Append labelled notes to the required root tracking files without rewriting concurrent/backend history.

Run the contract guard before and after relevant changes. On drift, inspect the backend changes and adapt frontend consumers before explicitly updating the baseline. Fingerprints alone do not prove type or runtime compatibility. Never test against or reset a running backend's retained review graphs implicitly.

End with actual commands/results, precise changed paths, limitations and the next frontend task, then stop for review. Do not describe fixtures or offline checks as live integration.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
