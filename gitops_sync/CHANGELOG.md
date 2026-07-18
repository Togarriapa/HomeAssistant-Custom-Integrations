# Changelog

## 0.1.1

- Adds an explicit one-time `initial_source` bootstrap.
- Defaults existing installations to `home_assistant` as the first source of truth.
- Exports the live configuration to `ha-sync` before any protected-branch apply.
- Forces the first export even if version 0.1.0 cached the local configuration hash.
- Refuses GitHub-led bootstrap when the protected branch has no managed configuration.
- Documents the exact adoption procedure for an already-running Home Assistant.

## 0.1.0

- Initial supervised Home Assistant app.
- Bidirectional protected-branch and pull-request synchronization.
- Exact Home Assistant version export through `.ha-version`.
- GitHub check gate for inbound commits.
- Strict path allowlist and sensitive-file denylist.
- YAML, symlink, binary, size, token, private-key, and plaintext-secret validation.
- Supervisor partial backup before inbound changes.
- Local rolling file backups with automatic rollback.
- Supervisor configuration check before restart.
- Post-restart health verification and rollback recovery.
