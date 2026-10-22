# Maintenance policy and Hermes handoff

The initial pilot is implemented by the current coding agent. Hermes handles light maintenance and alerts the owner to
upstream product decisions. The versioned [maintenance skill](../maintenance/skills/upstream-maintenance/SKILL.md) is
the execution guide; installing it on the actual Hermes host is an owner handoff step, not evidence that a remote
scheduler is already running.

## What runs nightly

GitHub Actions runs `Upstream intake` daily at **02:23 UTC**, with a manual dispatch available. It uses GitHub's
repository token, not AI or a vault secret. It resolves an immutable upstream branch tip and paginates only commits
touching `extensions/brew`. It opens or updates one issue labelled `upstream`.

The issue contains a durable discovery cursor and accumulated candidates. It is kept open even when everything is
addressed. Repeated runs with unchanged data do not write comments or open duplicate issues. A missing cursor, history
rewrite, malformed state, duplicate active intakes, or oversized report fails without advancing discovery. Workflow
failures need investigation, not a reset to the newest upstream SHA. GitHub may delay scheduled jobs; a scheduled
trigger is not an execution-time guarantee.

## Independent records

| Record         | Meaning                                               | Storage                                                |
| -------------- | ----------------------------------------------------- | ------------------------------------------------------ |
| Import         | Historical subtree and original authors               | Git history and `.upstream/history-map.txt`            |
| Discovery      | Commits seen and queued, including unimplemented work | Hidden JSON in the intake issue                        |
| Disposition    | Assess, adopt, or skip, with rationale and links      | `.upstream/decisions.json` through PRs                 |
| Implementation | Whether an implementation PR actually merged          | GitHub PR state and merge SHA, verified when reporting |

The imported baseline is immutable. Do not move it to claim a later change was adopted. Record a disposition using the
original full upstream SHA, for example:

```json
{
  "disposition": "adopt",
  "classification": "fix",
  "reason": "Corrects the existing tap-uninstall contract without adding features.",
  "pull_request": 12
}
```

An open, closed-unmerged, or feature-branch-only merged PR is never reported as applied to maintained main. Skipped
candidates remain traceable. If the intake approaches its size limit, archive only resolved entries into versioned
history in a reviewed PR; preserve unresolved candidates and repair the intake explicitly before discovery resumes.

## Hermes scope

Clearly understood patches, bug fixes, performance improvements, and docs may be adapted and merged autonomously within
required checks and reviews. Inspect the complete diff rather than trusting a commit subject or automated category.
Features, UI/design changes, intentional behavior changes, major dependency bumps, and uncertain or mixed patches become
assessment issues. Policy, CI, credentials, permissions, and signing changes also need owner assessment.

Assessment issues use a semantic title, `upstream:assessment`, source commit links, an explanation of the proposed
behavior, tradeoffs, a recommendation, and an AI implementation prompt for a separate session. The owner may apply
`upstream:approved`. Verify the latest label event was authored by `TurboCoder13`. The label does **not** authorize
Hermes to implement the feature.

No automated action installs or updates an extension on a Mac. The owner chooses when to install a tagged release or run
the checkout locally.

## Host prerequisites and limits

On the actual Hermes host, verify these before enabling unattended writes:

- Install the reviewed `agent-infra` version supporting `lgtm-raycast` and this skill. Keep the canonical GitHub origin
  and run `lgtm-ai doctor --quiet`.
- Provision read-only `ai-agents` service-account access privately in the agent environment. The App PEM is
  `op://ai-agents/lgtm-raycast-bot/private key`.
- Verify signed commits work unattended on that host. App authentication and commit signing are separate. The initial
  Mac signing probe does not establish remote-host signing readiness.
- Verify the host's existing AI subscription route. Do not use API-key helpers, unverified provider defaults, additional
  credits, or paid review services. Stop at limits. A vault credential's existence is not permission to spend.
- Configure one serialized Hermes queue run after intake discovery, for example 03:00 UTC, using the versioned skill.
  Limit each candidate to two repair attempts per run; leave blocked work open with a concrete explanation.

GitHub Actions performs discovery and deterministic verification. Hermes performs assessment and permitted coding using
its existing subscription. This pilot creates no new AI subscription, API integration, or T3 recurring schedule.

## Local verification

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

A local preview of the report is read-only:

```bash
# Supply a repository-scoped token privately through the environment.
python3 -m scripts.upstream.intake --dry-run
```

Never place tokens in command arguments, Git, issue bodies, screenshots, or logs.

## Initial validation baseline

The inherited suite has 417 passing tests. Whole-source coverage (including untested commands, hooks, and UI) starts at
27.40% statements, 24.31% branches, 25.47% functions, and 26.20% lines. Vitest enforces rounded-down floors to prevent
regressions; this is not a claim that imported application code meets a 90% coverage target. The new Python tracker is
gated at 90% and measures over 99%. Expand behavioral coverage in separate maintenance work.

Security scanning required bounded updates to stream-json 3.7.0, Vitest and its coverage provider 4.1.12, Vite 8.3.3,
and source-map-js 1.2.2. Prettier was updated to the supported 3.9 series so lintro actually runs it. Other resolved
upstream dependencies were retained. The adopt test fixtures use a nonexistent app directory so installed Mac apps
cannot change their outcome.

## Raycast CI compatibility

Raycast's CLI checks for `package-lock.json` only when `CI=true`; that check assumes the Store's npm packaging workflow.
This local-use edition installs from `bun.lock` with Bun's frozen-lockfile gate in lgtm-ci. The Raycast lint invocation
sets `CI=false` to omit only that incompatible npm-lock check. Manifest schema, upstream author/contributor, icon,
metadata, ESLint, and Prettier validation remain active. The egress policy explicitly permits `www.raycast.com:443` for
Raycast's schema and author-validation requests. No relaxed lint mode, fabricated npm lock, or parallel lock authority
is used.

The `.lgtm-ci-tooling/` directory is lgtm-ci's separately versioned workflow checkout, created only during CI. It is
excluded from this extension's lint and dependency discovery using `.lintro-ignore`; it is maintained and checked in its
own repository. Generated reports, dependencies, and build output are also excluded. Production extension code and both
committed lockfiles remain in scope.
