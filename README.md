# Brew — maintained local edition

Search, install, and manage Homebrew formulae and casks through Raycast. This standalone repository maintains the
upstream Brew extension using lintro and `lgtm-hq/lgtm-ci`. Product behavior is initially preserved.

This edition is installed locally and is not published to the Raycast Store. MIT attribution and filtered upstream
history are retained. See [provenance](docs/provenance.md) and the [maintenance policy](docs/maintenance.md).

## Install or update on your Mac

You control installation and updates. With Raycast, Homebrew, and Bun available:

```bash
git clone https://github.com/lgtm-raycast/brew.git
cd brew
bun install --frozen-lockfile
bun run dev
```

Raycast's development command builds and registers the local extension. Keep this checkout on the Mac. To update, choose
a release tag, check it out, run `bun install --frozen-lockfile`, and run `bun run dev` again. A release's source
archive can be extracted and used with the same Bun commands.

Upstream and local editions use the same command identities. Disable or remove the Store edition yourself if it
conflicts with your maintained installation. No workflow or Hermes task changes any Mac's installed extensions.

## Development and releases

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

Bun manages dependencies and runs all project scripts using the committed `bun.lock`. Raycast's CLI retains its Node
runtime; `bun run` launches the existing scripts without forcing a runtime replacement or creating another lockfile.
Strict TypeScript, Raycast validation, Python tracker tests, and coverage run in CI through pinned lgtm-ci workflows.

Version tags matching `package.json` run the release validation and publish a source bundle with checksums through
lgtm-ci. The release does not publish to npm or Raycast Store and does not install anything on a Mac.

Nightly upstream discovery updates the issue labelled `upstream`. Features and design decisions are reported for your
input; an owner-applied approval label queues separate implementation work. Hermes is limited to the documented light
maintenance policy. AI work uses existing subscriptions only.
