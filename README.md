# molecule-prompt-watchdog

Warns the agent when the user's prompt contains destructive or high-stakes keywords — before the agent acts on them. The agent receives additional context (a warning flag) injected at `UserPromptSubmit` hook time.

## How it works

The `UserPromptSubmit` hook scans the prompt for keywords across three severity tiers:

- **DESTROY** — `DROP TABLE`, `delete all`, `drop schema`, `truncate`
- **REWRITE** — `force push`, `--force` on git push
- **ALTER** — `rm -rf`, `chmod 000`, `chown root`

On a match, the hook emits `additionalContext` with a tiered warning so the agent acknowledges the risk before proceeding.

## Keywords

| Tier | Patterns |
|---|---|
| DESTROY | `DROP TABLE`, `delete all records`, `drop schema`, `truncate table` |
| REWRITE | `force push`, `--force` on git push, `git push +force` |
| ALTER | `rm -rf`, `rm -r /`, `chmod 000`, `chown root:root` |

## Install

### In org template (org.yaml)

```yaml
plugins:
  - molecule-prompt-watchdog
```

### From URL (community install)

```
github://Molecule-AI/molecule-ai-plugin-molecule-prompt-watchdog
```

## Usage

No configuration needed. Install and the hook is active for all sessions.

## Hooks

- **UserPromptSubmit** — scans prompt, injects warning context on keyword match

## Architecture

```
hooks/
  user-prompt-tag.py   # Python hook — regex scan, emit additionalContext
  user-prompt-tag.sh   # Shell wrapper
  _lib.py              # Shared helpers
adapters/
  claude_code.py       # Registers hook
settings-fragment.json # Declares UserPromptSubmit hook binding
```

## Runtime

- `claude_code` — primary

## Known issues

See [known-issues.md](known-issues.md).

## License

Business Source License 1.1 — © Molecule AI.
