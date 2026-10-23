# Brew — independently maintained Raycast fork

[![CI](https://github.com/lgtm-raycast/brew/actions/workflows/ci.yml/badge.svg)](https://github.com/lgtm-raycast/brew/actions/workflows/ci.yml)

Search, install, and manage Homebrew formulae and casks through Raycast. This is an independently maintained fork of the
[original Brew extension](https://github.com/raycast/extensions/tree/main/extensions/brew) in
[raycast/extensions](https://github.com/raycast/extensions), originally authored by
[nhojb](https://www.raycast.com/nhojb) with contributions from the Raycast community.

The extension's functionality, assets and original work come from those upstream authors. All author/contributor credits
remain in [the manifest](package.json) and the imported Git history. The original **MIT license and Raycast copyright**
remain in [LICENSE](LICENSE). Thank you to
[upstream contributors](https://github.com/raycast/extensions/commits/main/extensions/brew).

LGTM Raycast maintains this downstream using [lintro](https://github.com/lgtm-hq/py-lintro),
[lgtm-ci](https://github.com/lgtm-hq/lgtm-ci), and explicit upstream assessment/adoption. The pilot adopted upstream
snapshot [`645cb29`](https://github.com/raycast/extensions/commit/645cb29302e41f7730b0e68d84777feb0ad096a9). See
[provenance and history mapping](docs/provenance.md) for the exact import and authorship details.

This is a standalone downstream repository outside GitHub's fork network, maintained independently of Raycast. It is
installed locally and is not published to the Raycast Store.

## Project guides

- [Contributing](CONTRIBUTING.md) and [agent operating agreement](AGENTS.md).
- [Security and private reporting](SECURITY.md), [support](SUPPORT.md), and [code of conduct](CODE_OF_CONDUCT.md).
- [Upstream maintenance policy](docs/maintenance.md), [upstream development notes](docs/upstream-notes.md), and
  [change history](CHANGELOG.md).
- [Organization standards](https://github.com/lgtm-raycast/.github) and
  [current upstream intake](https://github.com/lgtm-raycast/brew/issues/3).

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
npm run lint
npm run build
```

Bun is the dependency/lockfile authority. The npm commands invoke Raycast's required scripts using those installed
dependencies; they do not create a second dependency lockfile. Strict TypeScript, Raycast validation, Python tracker
tests, and coverage run in CI through pinned lgtm-ci workflows.

Version tags matching `package.json` run the release validation and publish a source bundle with checksums through
lgtm-ci. The release does not publish to npm or Raycast Store and does not install anything on a Mac.

Nightly upstream discovery updates the issue labelled `upstream`. Features and design decisions are reported for your
input; an owner-applied approval label queues separate implementation work. Hermes is limited to the documented light
maintenance policy. AI work uses existing subscriptions only.
