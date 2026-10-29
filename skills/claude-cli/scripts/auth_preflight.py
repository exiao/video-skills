#!/usr/bin/env python3
"""Probe Claude authentication without exposing account or credential fields."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def emit(status, logged_in=None, method=None):
    result = {"status": status, "loggedIn": logged_in}
    if isinstance(method, str) and method in {"claude.ai", "api_key", "bedrock", "vertex", "foundry"}:
        result["authMethod"] = method
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare", type=Path, help="JSON from an earlier probe")
    args = parser.parse_args()
    previous = None
    if args.compare:
        try:
            previous = json.loads(args.compare.read_text())
            if not isinstance(previous, dict) or "loggedIn" not in previous:
                raise ValueError
            if previous["loggedIn"] is not None and type(previous["loggedIn"]) is not bool:
                raise ValueError
        except (OSError, ValueError):
            emit("invalid_previous_probe")
            return 2

    env = os.environ.copy()
    for name in (
        "ANTHROPIC_BASE_URL", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
    ):
        env.pop(name, None)
    try:
        probe = subprocess.run(
            ["claude", "auth", "status", "--json"], env=env, capture_output=True,
            text=True, timeout=20,
        )
        data = json.loads(probe.stdout)
        if not isinstance(data, dict) or type(data.get("loggedIn")) is not bool:
            raise ValueError
        if probe.returncode not in (0, 1) or probe.returncode == 1 and data["loggedIn"]:
            raise ValueError
    except FileNotFoundError:
        emit("claude_not_found")
        return 2
    except subprocess.TimeoutExpired:
        emit("probe_timeout")
        return 2
    except (OSError, ValueError):
        emit("probe_failed")
        return 2

    if not data["loggedIn"]:
        emit("login_unconfirmed", False, data.get("authMethod"))
        return 1
    status = "login_visible_after_retry" if previous and previous["loggedIn"] is not True else "authenticated"
    emit(status, True, data.get("authMethod"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
