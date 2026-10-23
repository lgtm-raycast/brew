"""Behavior tests for durable upstream intake, idempotency, and honest receipts."""

from __future__ import annotations

import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from assertpy import assert_that
from pytest import MonkeyPatch

from scripts.upstream import github, intake
from scripts.upstream.github import GitHub, GitHubError

BASE = "1" * 40
NEXT = "2" * 40
TIP = "3" * 40


class QueueGitHub(GitHub):  # pylint: disable=too-few-public-methods  # Implements the single exchange contract.
    """Return queued API fixtures while recording the exact request contract."""

    def __init__(self, responses: list[Any]) -> None:
        """Initialize API responses.

        Args:
            responses: JSON fixtures in expected request order.
        """
        super().__init__()
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        """Record an operation and return the next queued fixture.

        Args:
            method: HTTP method.
            path: Relative API path.
            payload: Optional write body.

        Returns:
            Next fixture response.
        """
        self.calls.append({"method": method, "path": path, "payload": payload})
        return self.responses.pop(0)


@pytest.fixture(name="config")
def source_config() -> dict[str, Any]:
    """Provide a minimal versioned upstream source and intake configuration."""
    return {
        "repository": "raycast/extensions",
        "ref": "main",
        "path": "extensions/brew",
        "baseline": BASE,
        "intake_label": "upstream",
    }


def commit(sha: str, subject: str = "fix: improve performance") -> dict[str, Any]:
    """Build an upstream GitHub commit fixture.

    Args:
        sha: Immutable original upstream commit identifier.
        subject: Upstream commit subject.

    Returns:
        A REST commit entry.
    """
    return {"sha": sha, "commit": {"message": subject}}


def test_discovery_pins_branch_and_filters_path(config: dict[str, Any]) -> None:
    """Pin pagination to a resolved tip and return unseen commits oldest first."""
    upstream = QueueGitHub([{"sha": TIP}, [commit(TIP), commit(NEXT), commit(BASE)]])
    found = intake.discover(client=upstream, config=config, previous=BASE)
    assert_that([item["sha"] for item in found]).is_equal_to([NEXT, TIP])
    assert_that(upstream.calls[1]["path"]).contains(f"sha={TIP}", "path=extensions%2Fbrew")


@pytest.mark.parametrize("commits", [[], [commit(NEXT)]])
def test_history_gap_never_advances(config: dict[str, Any], commits: list[dict[str, Any]]) -> None:
    """A rewrite or missing cursor must never be mistaken for a clean baseline."""
    with pytest.raises(ValueError, match="gap"):
        intake.discover(client=QueueGitHub([{"sha": TIP}, commits]), config=config, previous=BASE)


def test_discovery_reads_additional_pages(config: dict[str, Any]) -> None:
    """A cursor on a later page is found rather than dropping older changes."""
    upstream = QueueGitHub([{"sha": TIP}, [commit(NEXT)] * 100, [commit(BASE)]])
    assert_that(intake.discover(client=upstream, config=config, previous=BASE)).is_length(100)
    assert_that(upstream.calls[-1]["path"]).contains("page=2")


@pytest.mark.parametrize("response", [{"sha": "invalid"}, [], {"sha": TIP, "unused": 1}])
def test_discovery_rejects_invalid_api_data(config: dict[str, Any], response: object) -> None:
    """Malformed branches or commit pages fail before a cursor is persisted."""
    responses = [response, {}] if isinstance(response, dict) and response.get("sha") == TIP else [response]
    with pytest.raises((ValueError, TypeError)):
        intake.discover(client=QueueGitHub(responses), config=config, previous=BASE)


def test_discovery_rejects_malformed_commit(config: dict[str, Any]) -> None:
    """Do not publish unvalidated source identifiers as GitHub URLs."""
    with pytest.raises(ValueError, match="identifier"):
        intake.discover(client=QueueGitHub([{"sha": TIP}, [commit("invalid")]]), config=config, previous=BASE)


@pytest.mark.parametrize(
    "body",
    [
        intake.MARKER,
        intake.MARKER + '<!-- lgtm-upstream-state {"discovered":"bad","pending":[]} -->',
        '<!-- lgtm-upstream-state {"discovered":"' + BASE + '","pending":[{}]} -->',
    ],
)
def test_saved_state_corruption_is_not_silently_reset(body: str) -> None:
    """Preserve the last good intake rather than losing queued work on corruption."""
    with pytest.raises(ValueError):
        intake.read_state(body=body, baseline=BASE)


def test_read_state_without_issue_starts_at_imported_baseline() -> None:
    """The first run starts from the actual imported commit, not the branch tip."""
    assert_that(intake.read_state(body="", baseline=BASE)).is_equal_to({"discovered": BASE, "pending": []})


def test_duplicate_intakes_are_not_arbitrarily_merged() -> None:
    """Prevent one report from concealing another report's pending candidates."""
    downstream = QueueGitHub([[{"number": 1, "body": intake.MARKER}, {"number": 2, "body": intake.MARKER}]])
    with pytest.raises(ValueError, match="Multiple"):
        intake.find_intake(client=downstream, repository="lgtm-raycast/brew", label="upstream")


def test_pull_requests_do_not_count_as_intake_issues() -> None:
    """GitHub's issue listing includes PRs, which must never become the report."""
    downstream = QueueGitHub([[{"number": 1, "body": intake.MARKER, "pull_request": {}}]])
    assert_that(intake.find_intake(client=downstream, repository="lgtm-raycast/brew", label="upstream")).is_none()


def test_issue_search_pages_and_rejects_overflow(monkeypatch: MonkeyPatch) -> None:
    """Bound issue traversal and fail clearly rather than creating duplicates."""
    monkeypatch.setattr(intake, "MAX_PAGES", 1)
    with pytest.raises(ValueError, match="pagination"):
        intake.find_intake(client=QueueGitHub([[{}] * 100]), repository="lgtm-raycast/brew", label="upstream")
    with pytest.raises(TypeError, match="malformed"):
        intake.find_intake(client=QueueGitHub([{}]), repository="lgtm-raycast/brew", label="upstream")


@pytest.mark.parametrize(("merged", "expected"), [(True, "merged in #4"), (False, "not merged")])
def test_adoption_decision_is_distinct_from_actual_implementation(merged: bool, expected: str) -> None:
    """An adoption decision alone never claims that an open PR has landed."""
    status = intake.implementation_status(
        client=QueueGitHub([{"merged": merged, "merge_commit_sha": TIP, "base": {"ref": "main"}}]),
        repository="lgtm-raycast/brew",
        decision={"disposition": "adopt", "pull_request": 4},
    )
    assert_that(status).contains(expected)


@pytest.mark.parametrize(
    "decision", [{"disposition": "invalid"}, {"pull_request": -1}, {"pull_request": True}, {"pull_request": "4"}]
)
def test_receipts_reject_unknown_dispositions_and_invalid_prs(decision: dict[str, Any]) -> None:
    """A malformed receipt cannot masquerade as completed implementation."""
    with pytest.raises(ValueError):
        intake.implementation_status(client=QueueGitHub([]), repository="lgtm-raycast/brew", decision=decision)


def test_report_round_trips_discovery_without_claiming_adoption(config: dict[str, Any]) -> None:
    """Persist discovery and candidate text while keeping no-implementation explicit."""
    state = {"discovered": NEXT, "pending": [{"sha": NEXT, "subject": "fix | <script> -->"}]}
    body = intake.render_report(
        config=config, state=state, decisions={}, downstream=QueueGitHub([]), repository="lgtm-raycast/brew"
    )
    assert_that(intake.read_state(body=body, baseline=BASE)).is_equal_to(state)
    assert_that(body).contains("unclassified; no implementation", "&#124;", "&lt;script&gt;")


def test_report_size_limit_refuses_to_drop_state(config: dict[str, Any], monkeypatch: MonkeyPatch) -> None:
    """Oversized reports fail without silently discarding pending changes."""
    monkeypatch.setattr(intake, "MAX_BODY", 1)
    with pytest.raises(ValueError, match="too large"):
        intake.render_report(
            config=config,
            state={"discovered": BASE, "pending": []},
            decisions={},
            downstream=QueueGitHub([]),
            repository="lgtm-raycast/brew",
        )


@pytest.fixture(name="repository_root")
def source_repository_root(tmp_path: Path, config: dict[str, Any]) -> Path:
    """Write independent source config and adoption decisions for end-to-end runs."""
    (tmp_path / ".upstream").mkdir()
    (tmp_path / ".upstream/config.json").write_text(json.dumps(config))
    (tmp_path / ".upstream/decisions.json").write_text(json.dumps({"commits": {}}))
    return tmp_path


def test_full_cycle_creates_once_then_is_idempotent(repository_root: Path) -> None:
    """One active issue survives repeated identical discovery without extra writes."""
    upstream = QueueGitHub([{"sha": TIP}, [commit(NEXT), commit(BASE)]])
    downstream = QueueGitHub([[], {}])
    body = intake.run(root=repository_root, repository="lgtm-raycast/brew", upstream=upstream, downstream=downstream)
    assert_that(downstream.calls[-1]["method"]).is_equal_to("POST")
    again = QueueGitHub([[{"number": 7, "body": body}]])
    repeated = intake.run(
        root=repository_root,
        repository="lgtm-raycast/brew",
        upstream=QueueGitHub([{"sha": TIP}, [commit(NEXT)]]),
        downstream=again,
    )
    assert_that(repeated).is_equal_to(body)
    assert_that(again.calls).is_length(1)


def test_new_discovery_retains_earlier_unimplemented_work(repository_root: Path) -> None:
    """A later run appends to the queue instead of replacing earlier candidates."""
    state = {"discovered": NEXT, "pending": [{"sha": NEXT, "subject": "earlier"}]}
    body = intake.MARKER + "<!-- lgtm-upstream-state " + json.dumps(state) + " -->"
    downstream = QueueGitHub([[{"number": 7, "body": body}], {}])
    result = intake.run(
        root=repository_root,
        repository="lgtm-raycast/brew",
        upstream=QueueGitHub([{"sha": TIP}, [commit(TIP), commit(NEXT)]]),
        downstream=downstream,
    )
    assert_that([item["sha"] for item in intake.read_state(body=result, baseline=BASE)["pending"]]).is_equal_to(
        [NEXT, TIP]
    )
    assert_that(downstream.calls[-1]["method"]).is_equal_to("PATCH")


def test_dry_run_never_posts_an_issue(repository_root: Path) -> None:
    """Assessment previews remain read-only even when upstream has new changes."""
    downstream = QueueGitHub([[]])
    intake.run(
        root=repository_root,
        repository="lgtm-raycast/brew",
        upstream=QueueGitHub([{"sha": TIP}, [commit(NEXT), commit(BASE)]]),
        downstream=downstream,
        dry_run=True,
    )
    assert_that(downstream.calls).is_length(1)


def test_wrong_destination_is_rejected_before_api_calls(repository_root: Path) -> None:
    """Never leak a scoped credential into another repository's reporting flow."""
    downstream = QueueGitHub([])
    with pytest.raises(ValueError, match="only"):
        intake.run(root=repository_root, repository="other/brew", upstream=QueueGitHub([]), downstream=downstream)
    assert_that(downstream.calls).is_empty()


def test_github_client_keeps_auth_on_downstream_requests(monkeypatch: MonkeyPatch) -> None:
    """Public reads omit auth; downstream reporting uses an explicit credential."""
    calls: list[Any] = []

    def response(request: Any, timeout: int) -> BytesIO:
        """Record protocol fields and return an in-memory JSON response."""
        assert_that(timeout).is_equal_to(30)
        calls.append(request)
        return BytesIO(b'{"ok":true}')

    monkeypatch.setattr(github, "urlopen", response)
    public = GitHub()
    assert_that(public.request(method="GET", path="/repos/raycast/extensions")).is_equal_to({"ok": True})
    assert_that(calls[0].get_header("Authorization")).is_none()
    credential = "inert-fixture-value"
    private = GitHub(credential)
    private.request(method="POST", path="/repos/lgtm-raycast/brew/issues", payload={"title": "intake"})
    assert_that(calls[1].get_header("Authorization")).is_equal_to(f"Bearer {credential}")
    assert_that(json.loads(calls[1].data)).is_equal_to({"title": "intake"})


@pytest.mark.parametrize("path", ["https://other.example/path", "//other.example/path"])
def test_github_client_rejects_external_hosts(path: str) -> None:
    """Do not allow reporting credentials to be sent to a caller-selected host."""
    with pytest.raises(GitHubError, match="absolute path"):
        GitHub().request(method="GET", path=path)


def test_github_client_wraps_network_failures(monkeypatch: MonkeyPatch) -> None:
    """Surface a credential-free error without retrying against another identity."""

    def fail(*args: Any, **kwargs: Any) -> Any:
        """Simulate a failed fixed-host network request."""
        raise OSError("network failed")

    monkeypatch.setattr(github, "urlopen", fail)
    with pytest.raises(GitHubError, match="OSError"):
        GitHub().request(method="GET", path="/repos/raycast/extensions")


def test_cli_requires_scoped_token_and_prints_only_dry_run(monkeypatch: MonkeyPatch, capsys: Any) -> None:
    """Require explicit reporting auth and expose report text only for previews."""
    monkeypatch.setattr(sys, "argv", ["intake", "--dry-run"])
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        intake.main()
    monkeypatch.setenv("GH_TOKEN", "inert")
    monkeypatch.setattr(intake, "run", lambda **kwargs: "report preview")
    intake.main()
    assert_that(capsys.readouterr().out).contains("report preview")


def test_merge_into_feature_branch_is_not_reported_as_applied() -> None:
    """A stacked or staging merge is not implementation on maintained main."""
    status = intake.implementation_status(
        client=QueueGitHub([{"merged": True, "merge_commit_sha": TIP, "base": {"ref": "feature/staging"}}]),
        repository="lgtm-raycast/brew",
        decision={"disposition": "adopt", "pull_request": 4},
    )
    assert_that(status).contains("not applied to main")
    assert_that(status).does_not_contain("merged in #4")
