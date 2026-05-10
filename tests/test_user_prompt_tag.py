#!/usr/bin/env python3
"""Unit tests for user-prompt-tag.py hook."""
import io
import json
import os
import sys
from unittest import mock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))


def run_hook(prompt):
    """Simulate UserPromptSubmit hook invocation."""
    stdin_data = json.dumps({"prompt": prompt})
    stdout = io.StringIO()
    stderr = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(stdin_data)), \
         mock.patch("sys.stdout", stdout), \
         mock.patch("sys.stderr", stderr), \
         mock.patch("sys.exit", lambda code: None):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "prompt_mod",
            os.path.join(os.path.dirname(__file__), "..", "hooks", "user-prompt-tag.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
    return stdout.getvalue(), stderr.getvalue()


def parse_context(output):
    """Return the additionalContext from an emit payload, or None."""
    if not output.strip():
        return None
    try:
        payload = json.loads(output.strip())
        return payload.get("additionalContext")
    except json.JSONDecodeError:
        return None


class TestDestructiveKeywordWarnings:
    """Tests for force-push and destructive operation detection."""

    def test_warns_on_force_push(self):
        output, _ = run_hook("Please force push to main to restore the branch")
        ctx = parse_context(output)
        assert ctx is not None
        assert "force-push" in ctx.lower() or "force push" in ctx.lower()

    def test_warns_on_git_push_f(self):
        output, _ = run_hook("git push -f origin feature")
        ctx = parse_context(output)
        assert ctx is not None

    def test_warns_on_delete_all(self):
        output, _ = run_hook("delete all the records from the database")
        ctx = parse_context(output)
        assert ctx is not None
        assert "all" in ctx.lower() or "destructive" in ctx.lower()

    def test_warns_on_drop_table(self):
        output, _ = run_hook("drop table users cascade")
        ctx = parse_context(output)
        assert ctx is not None
        assert "sql" in ctx.lower() or "migration" in ctx.lower()

    def test_warns_on_truncate(self):
        output, _ = run_hook("truncate the audit log")
        ctx = parse_context(output)
        assert ctx is not None

    def test_warns_on_direct_main_push(self):
        output, _ = run_hook("commit directly to main without a PR")
        ctx = parse_context(output)
        assert ctx is not None
        assert "main" in ctx.lower()


class TestBulkCloseWarnings:
    """Tests for bulk-close detection."""

    def test_warns_on_close_all_issues(self):
        output, _ = run_hook("close all issues that are older than 30 days")
        ctx = parse_context(output)
        assert ctx is not None
        assert "bulk" in ctx.lower() or "close" in ctx.lower()

    def test_warns_on_close_all_prs(self):
        output, _ = run_hook("close every PR in the repo")
        ctx = parse_context(output)
        assert ctx is not None

    def test_no_warning_for_single_close(self):
        output, _ = run_hook("close issue #123")
        ctx = parse_context(output)
        # Single close should not trigger bulk warning
        assert ctx is None or "bulk" not in ctx.lower()


class TestNoWarningForSafePrompts:
    """Safe prompts must not trigger warnings."""

    def test_no_warning_for_read_only(self):
        output, _ = run_hook("Show me the contents of src/main.py and explain what it does")
        ctx = parse_context(output)
        assert ctx is None

    def test_no_warning_for_create_branch(self):
        output, _ = run_hook("Create a new feature branch from main and add the new endpoint")
        ctx = parse_context(output)
        assert ctx is None

    def test_no_warning_for_normal_commit(self):
        output, _ = run_hook("commit my changes to the feature branch")
        ctx = parse_context(output)
        assert ctx is None

    def test_no_warning_for_empty_prompt(self):
        output, _ = run_hook("")
        ctx = parse_context(output)
        assert ctx is None

    def test_no_warning_for_test_query(self):
        output, _ = run_hook("run the test suite and tell me what failed")
        ctx = parse_context(output)
        assert ctx is None


class TestContextFormat:
    """Tests for the format of emitted additionalContext."""

    def test_context_includes_watchdog_header(self):
        output, _ = run_hook("force push to main")
        ctx = parse_context(output)
        assert ctx is not None
        assert "⚠" in ctx or "warning" in ctx.lower() or "Prompt-watchdog" in ctx

    def test_context_includes_careful_mode_reminder(self):
        output, _ = run_hook("drop table users")
        ctx = parse_context(output)
        assert ctx is not None
        assert "careful-mode" in ctx.lower() or "destructive" in ctx.lower()