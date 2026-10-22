#!/usr/bin/env bash
set -euo pipefail
bash scripts/ci/raycast-check.sh
bash scripts/ci/package.sh
