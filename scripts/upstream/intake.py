#!/usr/bin/env python3
"""Discover upstream subtree changes and maintain one durable intake issue."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from scripts.upstream.github import GitHub

MARKER = "<!-- lgtm-upstream-intake:v1 -->"
STATE = re.compile(r"<!-- lgtm-upstream-state (\{.*?\}) -->", re.DOTALL)
SHA = re.compile(r"[0-9a-f]{40}")
MAX_PAGES = 20
MAX_BODY = 60_000


def read_state(body: str, baseline: str) -> dict[str, Any]:
    """Read durable discovery independently of adoption decisions.

    Args:
        body: Existing issue body.
        baseline: Initial imported upstream commit.

    Returns:
        Last discovered path commit and accumulated pending candidates.

    Raises:
        ValueError: When saved state is malformed; never silently reset it.
    """
    match = STATE.search(body)
    if not match:
        if MARKER in body:
            raise ValueError("Intake issue lost its discovery state; repair it before advancing")
        return {"discovered": baseline, "pending": []}
    state = json.loads(match.group(1))
    if (
        not isinstance(state, dict)
        or not isinstance(state.get("discovered"), str)
        or not SHA.fullmatch(state["discovered"])
        or not isinstance(state.get("pending"), list)
        or any(not isinstance(item, dict) or not SHA.fullmatch(str(item.get("sha", ""))) for item in state["pending"])
    ):
        raise ValueError("Invalid discovery state")
    return state


def discover(client: GitHub, config: dict[str, Any], previous: str) -> list[dict[str, str]]:
    """Find path commits newer than the last successful discovery.

    Args:
        client: Public, unauthenticated upstream client.
        config: Versioned upstream location.
        previous: Last discovered path commit, never a guessed timestamp.

    Returns:
        Newly discovered commits in oldest-first order.

    Raises:
        GitHubError: When a page or branch cannot be read.
        ValueError: On a history gap, rewrite, or pagination limit.
        TypeError: When upstream returns an invalid list.
    """
    repository = config["repository"]
    tip = client.request(method="GET", path=f"/repos/{repository}/commits/{config['ref']}")
    tip_sha = tip.get("sha", "") if isinstance(tip, dict) else ""
    if not SHA.fullmatch(tip_sha):
        raise ValueError("Upstream branch did not resolve to an immutable commit")
    candidates: list[dict[str, str]] = []
    for page in range(1, MAX_PAGES + 1):
        query = urlencode({"sha": tip_sha, "path": config["path"], "per_page": 100, "page": page})
        commits = client.request(method="GET", path=f"/repos/{repository}/commits?{query}")
        if not isinstance(commits, list):
            raise TypeError("Upstream commit list is malformed")
        for commit in commits:
            source_sha = commit.get("sha", "")
            if not SHA.fullmatch(source_sha):
                raise ValueError("Upstream returned a malformed commit identifier")
            if source_sha == previous:
                return list(reversed(candidates))
            candidates.append({"sha": source_sha, "subject": commit["commit"]["message"].splitlines()[0]})
        if len(commits) < 100:
            break
    raise ValueError("Previous discovery is missing from path history; refusing to advance across a gap")


def find_intake(client: GitHub, repository: str, label: str) -> dict[str, Any] | None:
    """Locate the one open intake, refusing to silently choose duplicates.

    Args:
        client: Downstream repository client.
        repository: Destination owner/name.
        label: Dedicated intake label.

    Returns:
        Existing intake or None.

    Raises:
        ValueError: When multiple active intake issues or too many pages exist.
        TypeError: When the issue list is malformed.
    """
    matches: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        query = urlencode({"state": "open", "labels": label, "per_page": 100, "page": page})
        issues = client.request(method="GET", path=f"/repos/{repository}/issues?{query}")
        if not isinstance(issues, list):
            raise TypeError("Downstream issue list is malformed")
        matches.extend(issue for issue in issues if "pull_request" not in issue and MARKER in (issue.get("body") or ""))
        if len(issues) < 100:
            if len(matches) > 1:
                raise ValueError("Multiple active upstream intake issues require reconciliation")
            return matches[0] if matches else None
    raise ValueError("Issue pagination limit exceeded")


def implementation_status(client: GitHub, repository: str, decision: dict[str, Any]) -> str:
    """Report actual merged implementation separately from a recorded decision.

    Args:
        client: Downstream repository client.
        repository: Destination owner/name.
        decision: Versioned disposition and optional implementation PR.

    Returns:
        Human-readable decision and independently verified implementation state.

    Raises:
        ValueError: When a receipt references an invalid PR number.
    """
    disposition = decision.get("disposition", "unclassified")
    if disposition not in {"unclassified", "assess", "adopt", "skip"}:
        raise ValueError("Unknown upstream disposition")
    number = decision.get("pull_request")
    if number is None:
        return f"{disposition}; no implementation recorded"
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError("Implementation receipt requires a positive PR number")
    pull = client.request(method="GET", path=f"/repos/{repository}/pulls/{number}")
    if pull.get("merged") is True:
        if pull.get("base", {}).get("ref") != "main":
            return f"{disposition}; #{number} merged outside main; not applied to main"
        return f"{disposition}; merged in #{number} ({pull['merge_commit_sha'][:7]})"
    return f"{disposition}; #{number} is not merged"


def render_report(
    config: dict[str, Any],
    state: dict[str, Any],
    decisions: dict[str, Any],
    downstream: GitHub,
    repository: str,
) -> str:
    """Render data and receipts without treating discovery as adoption.

    Args:
        config: Upstream location and baseline.
        state: Durable discovery cursor and candidate list.
        decisions: Versioned per-commit dispositions.
        downstream: Client used to verify implementation receipts.
        repository: Destination owner/name.

    Returns:
        The complete intake body, including its durable state.

    Raises:
        ValueError: When the report would exceed GitHub's issue limit.
    """
    lines = [
        MARKER,
        "## Upstream intake",
        "",
        f"Source: [{config['repository']}](https://github.com/{config['repository']}) / `{config['path']}`.",
        f"Imported baseline: `{config['baseline']}`.",
        f"Last discovered path commit: `{state['discovered']}`.",
        "",
        (
            "Discovery does not imply adoption. Hermes assesses each patch; "
            "features, design changes, and uncertainty need owner input."
        ),
        (
            "An owner-applied `upstream:approved` label queues a separate implementation "
            "session; it never authorizes Hermes feature work."
        ),
        "",
        "| Commit | Upstream change | Disposition and implementation |",
        "| --- | --- | --- |",
    ]
    for item in state["pending"]:
        source_sha = item["sha"]
        decision = decisions.get(source_sha, {})
        status = implementation_status(client=downstream, repository=repository, decision=decision)
        subject = html.escape(str(item.get("subject", ""))).replace("|", "&#124;").replace("\n", " ")
        lines.append(
            f"| [{source_sha[:7]}](https://github.com/{config['repository']}/commit/{source_sha}) "
            f"| {subject} | {status} |"
        )
    if not state["pending"]:
        lines.extend(["", "No new path commits have been discovered."])
    lines.extend(
        [
            "",
            "<!-- lgtm-upstream-state "
            + json.dumps(state, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e")
            + " -->",
            "",
        ]
    )
    body = "\n".join(lines)
    if len(body) > MAX_BODY:
        raise ValueError("Intake is too large; archive dispositions without dropping pending work before advancing")
    return body


def run(root: Path, repository: str, upstream: GitHub, downstream: GitHub, dry_run: bool = False) -> str:
    """Perform an idempotent discovery/report cycle without touching source code.

    Args:
        root: Repository root containing versioned configuration and decisions.
        repository: Explicit allowed downstream owner/name.
        upstream: Public upstream client.
        downstream: Scoped reporting client.
        dry_run: Render only without any GitHub writes.

    Returns:
        Report body for verification or dry-run output.

    Raises:
        ValueError: On invalid config, state, or receipt data.
    """
    if repository != "lgtm-raycast/brew":
        raise ValueError("This pilot reports only to lgtm-raycast/brew")
    config = json.loads((root / ".upstream/config.json").read_text())
    decisions = json.loads((root / ".upstream/decisions.json").read_text())["commits"]
    issue = find_intake(client=downstream, repository=repository, label=config["intake_label"])
    state = read_state(body=(issue.get("body") or "") if issue else "", baseline=config["baseline"])
    commits = discover(client=upstream, config=config, previous=state["discovered"])
    known = {item["sha"] for item in state["pending"]}
    state["pending"].extend(item for item in commits if item["sha"] not in known)
    if commits:
        state["discovered"] = commits[-1]["sha"]
    body = render_report(config=config, state=state, decisions=decisions, downstream=downstream, repository=repository)
    if not dry_run:
        if issue:
            if body != issue.get("body"):
                downstream.request(
                    method="PATCH", path=f"/repos/{repository}/issues/{issue['number']}", payload={"body": body}
                )
        else:
            downstream.request(
                method="POST",
                path=f"/repos/{repository}/issues",
                payload={
                    "title": "chore(upstream): Brew intake and adoption status",
                    "labels": [config["intake_label"]],
                    "body": body,
                },
            )
    return body


def main() -> None:
    """Run the CLI using only the repository-scoped Actions or App credential."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "lgtm-raycast/brew"))
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        parser.error("a repository-scoped GH_TOKEN or GITHUB_TOKEN is required")
    body = run(
        root=Path(__file__).resolve().parents[2],
        repository=arguments.repository,
        upstream=GitHub(),
        downstream=GitHub(token),
        dry_run=arguments.dry_run,
    )
    if arguments.dry_run:
        print(body)


if __name__ == "__main__":
    main()
