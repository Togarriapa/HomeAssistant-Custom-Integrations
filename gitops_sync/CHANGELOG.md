# Changelog

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
