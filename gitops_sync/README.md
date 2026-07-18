# Home Assistant GitOps Sync

A fail-safe Home Assistant app for bidirectional synchronization of declarative configuration with GitHub.

## Core behavior

- **Home Assistant → GitHub:** exports allowlisted local changes to `ha-sync` and opens a pull request.
- **GitHub → Home Assistant:** applies only the protected branch after required GitHub checks pass.
- Creates a Supervisor backup and a local rollback copy before every inbound apply.
- Runs the Supervisor configuration check before restart.
- Verifies Home Assistant health after restart and automatically restores the previous files on failure.
- Refuses secrets, `.storage`, databases, logs, private keys, binary files, symlinks, and suspicious plaintext credentials.

See [DOCS.md](DOCS.md) for setup, branch protection, token permissions, safety boundaries, and recovery instructions.
