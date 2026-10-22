"""Small fixed-host GitHub client for read-only upstream and issue reporting."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class GitHubError(RuntimeError):
    """Raised when an API request cannot be completed safely."""


class GitHub:
    """Call GitHub without exposing credentials or following arbitrary hosts."""

    def __init__(self, token: str | None = None) -> None:
        """Store an optional credential for the downstream installation.

        Args:
            token: Repository-scoped token; omit for public upstream reads.
        """
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """Exchange JSON with the fixed GitHub API host.

        Args:
            method: HTTP verb.
            path: Absolute API path, never an arbitrary URL.
            payload: Optional request body.

        Returns:
            Parsed JSON response.

        Raises:
            GitHubError: On invalid paths, failed requests, or malformed JSON.
        """
        if not path.startswith("/") or path.startswith("//"):
            raise GitHubError("GitHub API requires an absolute path")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "lgtm-raycast-upstream-tracker",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(
            url=f"https://api.github.com{path}",
            method=method,
            headers=headers,
            data=json.dumps(payload).encode() if payload is not None else None,
        )
        try:
            with urlopen(request, timeout=30) as response:  # nosec B310 - fixed HTTPS host
                return json.loads(response.read())
        except (HTTPError, OSError, ValueError) as error:
            raise GitHubError(f"GitHub {method} {path} failed: {type(error).__name__}") from error
