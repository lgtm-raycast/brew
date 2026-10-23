# Contributing

This is the independently maintained local-use Brew extension. Keep upstream attribution, preserve product intent, and
keep changes focused. See [the original extension](https://github.com/raycast/extensions/tree/main/extensions/brew),
[provenance](docs/provenance.md), and [LICENSE](LICENSE) for original authorship and MIT terms. Read
[AGENTS.md](AGENTS.md) and [the maintenance policy](docs/maintenance.md) first.

## Verification

Use the committed Bun and uv lockfiles:

```bash
bun install --frozen-lockfile
uv sync --frozen
uv run lintro fmt
uv run lintro chk
uv run lintro tst
bun run test:coverage
npm run lint
npm run build
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

## Issues and review

Follow the [organization issue conventions](https://github.com/lgtm-raycast/.github/blob/main/CONTRIBUTING.md): semantic
title, Summary, Problem, Proposed Solution, Implementation Notes and Benefits where applicable, plus acceptance
criteria/references. Code-change issues receive a separate AI Implementation Prompt comment in a real fenced text block,
with Requirements, Files to Modify, Tests and Before Submitting sections. All issues are assigned to `TurboCoder13` and
carry appropriate shared category/priority labels; upstream approval labels retain their policy meaning.

Use `.github/PULL_REQUEST_TEMPLATE.md`. Under `## Closes`, write `- Closes #N` for fully resolved scope or
`- Relates to #N` for partial work. Every applicable check must be green, required reviews satisfied and every
actionable review thread addressed and resolved. Both required CI gates and strict main protection apply; no
administrative bypass. Done means merged to main, with post-merge CI verified.

Dependency updates extend the shared organization Renovate preset. They require the same CI/review policy; no dependency
automation may merge over failures. See [organization repository setup][setup] for the required service installation and
shared metadata action. A repository config does not install the Renovate App.

## Community and license

Follow [the code of conduct](CODE_OF_CONDUCT.md), use [support](SUPPORT.md) for help and report vulnerabilities
[privately](SECURITY.md). Contributions use this repository's MIT license. Preserve the original Raycast notice,
manifest author/contributors and imported history. Downstream tooling ownership does not replace upstream credit.

[setup]: https://github.com/lgtm-raycast/.github/blob/main/docs/repository-setup.md
