#!/usr/bin/env bash
# Release a source bundle for owner-controlled local installation.
set -euo pipefail
version=$(node -p 'require("./package.json").version')
if [[ ${GITHUB_REF_TYPE:-} == tag && ${GITHUB_REF_NAME:-} != "v${version}" ]]; then
	echo "Release tag must match package.json version" >&2
	exit 1
fi
mkdir -p artifacts
git archive --format=tar.gz --prefix="brew-${version}/" --output="artifacts/brew-${version}.tar.gz" HEAD
