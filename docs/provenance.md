# Upstream provenance

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
