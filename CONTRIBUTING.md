# Contributing

This is the independently maintained local-use Brew extension. Keep upstream attribution, preserve product intent, and
keep changes focused. Read [AGENTS.md](AGENTS.md) and [the maintenance policy](docs/maintenance.md) first.

## Verification

Use the committed Bun and uv lockfiles:

```bash
bun install --frozen-lockfile
uv sync --frozen
uv run lintro fmt
uv run lintro chk
uv run lintro tst
bun run test:coverage
bun run lint
bun run build
```

Raycast's lint/build owns extension-specific validation and runs last. Do not modify installed apps or run real Homebrew
mutations as tests. Unit fixtures must be independent of a machine's installed applications.

Use signed semantic commits and open a PR. CI checks and review threads must be satisfied before squash merging. Agent
writes use the configured private App through `lgtm-ai`; a failed bot command is not permission to use personal
credentials. Use only existing AI subscriptions; paid API/review fallbacks are not authorized.

## Upstream changes

Inspect complete path-scoped upstream diffs. Record original SHAs, rationale, dispositions, and implementation PR links
in `.upstream/decisions.json`. Discovery and implementation are separate: a queued upstream commit has not landed until
its implementation PR actually merges.

Hermes handles light maintenance only. Features, design changes, and uncertain changes need owner assessment and a
separate implementation session. Never apply `upstream:approved` on the owner's behalf.

This repository does not publish to Raycast Store or npm. Local installation and updates on each Mac are the owner's
task.
