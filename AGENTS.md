# Brew downstream operating agreement

## House standards

Use Bun with the committed `bun.lock`; Python tooling uses uv. Run `uv run lintro fmt`, `uv run lintro chk`,
`uv run lintro tst`, `bun run test:coverage`, then `bun run lint` and `bun run build`. Raycast owns extension-specific
rules. CI uses SHA-pinned `lgtm-hq/lgtm-ci`. Run scripts with Bun; do not force the Raycast CLI onto Bun with `--bun`.
Store-specific npm guidance in generic skills does not apply to this local-use fork.

Apply the shared `stand-general`, `stand-ts`, `stand-py`, `stand-ci`, `lint`, and `raycast` skills when available.
TypeScript is strict. Raycast command modules and configuration files retain framework-required default exports. React's
existing error boundary retains the class required by its lifecycle API.

The maintained source begins with imported upstream history. Initial adoption changes tooling and formatting while
preserving extension behavior. MIT notices, upstream authors, and the original-to-filtered history map must be retained.

Imported product-specific findings remain in [upstream development notes](docs/upstream-notes.md). Use them as
historical context; this agreement takes precedence over upstream tooling instructions.

## Identity and merges

Canonical origin is `https://github.com/lgtm-raycast/brew.git`. Use the configured `lgtm-raycast-bot` through `lgtm-ai`
for agent commits, pushes, and GitHub writes. Run `lgtm-ai doctor --quiet` before the first write each session. Never
fall back to personal credentials. Preserve the configured human committer and signature. Deterministic Actions
workflows use their repository-scoped `GITHUB_TOKEN`.

Use signed semantic commits and squash PR merges. Both `Required CI` and `gate / ✅ All Checks Passed` must pass, every
other check must be green, required reviews must be satisfied, and review threads must be resolved. Review the final
diff and record the exact reviewed head before autonomous merging. Do not weaken branch protection or use an
administrative merge to evade it. Verify post-merge main CI before handback. Use `.github/PULL_REQUEST_TEMPLATE.md`;
fully resolved issues require `- Closes #N` under `## Closes`.

## Standing scope

The [maintenance policy](docs/maintenance.md) is authoritative for Hermes. Features, design changes, intentional
behavior changes, and uncertain/mixed upstream changes require assessment. An owner-applied approval label queues a
separate implementation session and never expands Hermes's scope.

Existing AI subscriptions only; no additional API costs, paid review calls, or credit purchases. Stop on allowance
exhaustion. No autonomous installation or updates on the owner's Macs. This repository is public and is used locally;
Raycast Store publishing is outside scope.
