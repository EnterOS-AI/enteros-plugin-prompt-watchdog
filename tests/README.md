# Test Coverage — molecule-prompt-watchdog

## What We Test

This plugin has **executable hooks** (Python), so it warrants real unit tests.

| File | What | How |
|------|------|-----|
| `hooks/user-prompt-tag.py` | Destructive keyword detection, bulk-close detection, safe-prompt passthrough | pytest unit tests with mocked stdin/stdout |

## Test Categories

- **DestructiveKeywordWarnings** (6 tests): `force-push`, `git push -f`, `delete all`, `drop table`, `truncate`, direct main push
- **BulkCloseWarnings** (3 tests): `close all issues`, `close every PR`, single close passthrough
- **NoWarningForSafePrompts** (5 tests): read-only, branch creation, normal commit, empty prompt, test query
- **ContextFormat** (2 tests): watchdog header present, careful-mode reminder present

## Running Tests

```bash
python -m pytest tests/ -v
```
