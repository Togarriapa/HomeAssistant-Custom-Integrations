# Home Assistant GitOps Sync

A fail-safe Home Assistant app for bidirectional synchronization of declarative configuration with GitHub.

## Core behavior

- **Existing Home Assistant → GitHub:** with `initial_source: home_assistant`, the first run exports the current live allowlisted configuration to `ha-sync` and opens a pull request before any protected-branch deployment.
- **Home Assistant → GitHub:** later local changes continue to update `ha-sync` and its pull request.
- **GitHub → Home Assistant:** applies only the protected branch after required GitHub checks pass.
- Creates a Supervisor backup and a local rollback copy before every inbound apply.
- Runs the Supervisor configuration check before restart.
- Verifies Home Assistant health after restart and automatically restores the previous files on failure.
- Refuses secrets, `.storage`, databases, logs, private keys, binary files, symlinks, and suspicious plaintext credentials.

You do not run `git init` inside Home Assistant OS. The app maintains its own private clone and maps only the approved Home Assistant configuration paths.

See [DOCS.md](DOCS.md) for setup, branch protection, token permissions, first-run adoption, safety boundaries, and recovery instructions.
