# Upstream provenance and authorship

This repository is an independently maintained fork/downstream of
[Raycast Brew](https://github.com/raycast/extensions/tree/main/extensions/brew), originally authored by
[nhojb](https://www.raycast.com/nhojb) and the Raycast community. It is separate from the GitHub fork network.

Source: <https://github.com/raycast/extensions>, subtree `extensions/brew`. Requested snapshot:
`645cb29302e41f7730b0e68d84777feb0ad096a9`.

The import retains all 85 commits relevant to that subtree through the requested snapshot, including original
author/committer names, dates, and messages. Paths were moved to repository root with `git fast-export` and
`git filter-repo`. `.upstream/history-map.txt` maps original upstream SHAs to filtered SHAs. The requested snapshot's
subtree tree hash was verified identical after extraction.

Filtering changes commit hashes; original cryptographic commit signatures cannot remain valid. Follow the original SHA
links to inspect upstream verification. New downstream commits use the bot author and verified human signature.

To exercise a real integration cycle, the initial maintained branch starts at
`97f2b1aadec7437d898fe4948245a8b924883995`, immediately before the requested snapshot. The first intake and adoption PR
apply the actual screenshot update from the requested snapshot. The `upstream-import/<full-sha>` tag preserves the
complete filtered snapshot independently of this pilot cycle.

The original MIT license and Raycast copyright remain in `LICENSE`. Manifest author and contributors retain upstream
attribution. Downstream maintenance is owned by `lgtm-raycast`; this is an independently maintained local-use edition.

## Original and downstream credit

The extension's [manifest author and contributor list](../package.json) remains upstream's attribution, and the filtered
history preserves all imported author/committer names, timestamps and commit messages. Inspect the
[upstream path history](https://github.com/raycast/extensions/commits/main/extensions/brew) for original commits. The
repository-level [MIT license](../LICENSE) preserves `Copyright (c) 2021 Raycast`; copied assets and code retain those
terms. New maintenance does not transfer or overwrite upstream authorship.

LGTM Raycast owns downstream decisions, tooling, CI and support for this edition. This is not an official Raycast
release and does not imply endorsement by the original authors. Upstream features are assessed independently;
`.upstream/decisions.json` records dispositions and merged implementation receipts rather than inventing adopted
commits.

The pilot's real snapshot adoption merged in [PR #5](https://github.com/lgtm-raycast/brew/pull/5). The preceding
baseline description above records the historical import sequence; it is not the current adoption cursor. The
[durable intake](https://github.com/lgtm-raycast/brew/issues/3) tracks subsequent discoveries and implementation status.
