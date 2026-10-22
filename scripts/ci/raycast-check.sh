#!/usr/bin/env bash
# Raycast validation is intentionally last: it owns extension-specific rules.
set -euo pipefail
npm run lint
npm run build
