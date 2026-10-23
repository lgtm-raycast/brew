#!/usr/bin/env bash
# Raycast validation is intentionally last: it owns extension-specific rules.
set -euo pipefail
# Raycast's CI-only lock check requires npm's Store lockfile. This local-use
# edition uses Bun's frozen lock instead; keep every other Raycast check active.
CI=false bun run lint
bun run build
# Keep the manifest-derived declarations available to the independent lint job.
# Raycast's generator is authoritative; this catches stale committed output.
git diff --exit-code -- raycast-env.d.ts
