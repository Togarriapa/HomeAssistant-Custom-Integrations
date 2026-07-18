# Home Assistant GitOps Sync

Bidirectional Git synchronization for **declarative** Home Assistant configuration, designed so that neither GitHub nor a local UI edit can silently replace the protected configuration.

## Safety model

No automation can mathematically guarantee that a configuration can never fail. This app instead uses multiple independent barriers:

1. GitHub changes are read only from the configured protected branch.
2. The target commit must have successful GitHub checks when `require_github_checks` is enabled.
3. Only explicitly allowlisted `managed_paths` are synchronized.
4. `.storage`, `secrets.yaml`, databases, logs, private keys, backups, and cloud/authentication files are hard-blocked.
5. Symlinks, path traversal, oversized files, binary files, malformed YAML, obvious tokens, private keys, and likely plaintext credentials are rejected.
6. A Home Assistant partial backup is created before any inbound apply.
7. A second app-local file rollback copy is created before modification.
8. The files are applied and Home Assistant's Supervisor configuration check must succeed before restart.
9. After restart, the app polls the authenticated Home Assistant API. If Home Assistant does not become healthy, the previous files are restored and Home Assistant is restarted again.
10. Changes made in Home Assistant are pushed to a separate branch and PR; the protected branch is never directly overwritten by the app.

## Current scope

Version 0.1.1 safely tracks UTF-8 declarative configuration such as:

- `configuration.yaml`
- UI-created `automations.yaml`, `scripts.yaml`, and `scenes.yaml`
- packages, blueprints, themes, and YAML dashboards

Binary assets are intentionally outside the default scope. They can be added later through a separately validated asset channel without weakening configuration validation.

Home Assistant's `.storage` directory is intentionally blocked. It contains internal registries, authentication data, integration credentials, refresh tokens, and implementation-specific state. Treating those JSON files as ordinary mergeable Git configuration can corrupt registries or leak credentials.

A future encrypted state channel can back up selected `.storage` records, but it must remain separate from the automatically applied declarative branch.

## GitHub token

Create a fine-grained token restricted to the private configuration repository with:

- Contents: Read and write
- Pull requests: Read and write
- Commit statuses: Read
- Actions: Read

Store it only in the app configuration. The app uses `GIT_ASKPASS`, keeps the clean repository URL in Git, masks the token from Git errors, and stores its local token file with mode `0600` inside private app data.

## Installation for an existing Home Assistant

You do **not** initialize Git inside Home Assistant OS and you do not copy `/config` manually.

1. In Home Assistant, open **Settings → Apps → App store → Repositories**.
2. Add `https://github.com/Togarriapa/HomeAssistant-Custom-Integrations`.
3. Install **Home Assistant GitOps Sync** version 0.1.1 or newer.
4. Enter the fine-grained GitHub token.
5. Keep `repository: Togarriapa/HomeAssistant_Repo`.
6. Keep `initial_source: home_assistant` for an already-running installation.
7. Keep `delete_removed: false` during initial adoption.
8. Start the app and inspect its logs.

## First synchronization from an existing Home Assistant

With `initial_source: home_assistant`, first start performs a one-time protected bootstrap:

- The protected `main` branch is inspected but is not applied to Home Assistant.
- The app exports only the allowlisted live files to `ha-sync`.
- Secrets, `.storage`, databases, logs, keys, and runtime files are excluded.
- The exact installed Home Assistant version is written to `.ha-version`.
- A pull request from `ha-sync` to `main` is opened.
- GitHub Actions validates the exported configuration using the matching Home Assistant container version.
- You review and merge the PR.
- The merged, validated commit then becomes the protected synchronization baseline.

This first export is forced even when v0.1.0 previously cached the local configuration hash.

## Alternative bootstrap from GitHub

Use `initial_source: github` only when the protected repository already contains the intended configuration and GitHub must replace the matching managed paths in Home Assistant.

The app refuses this mode when the protected branch has no managed configuration. Before applying it creates a Supervisor backup and local rollback, checks the GitHub status, validates the files, runs the Home Assistant configuration check, and verifies health after restart.

## Recommended branch protection

Protect `main` in `Togarriapa/HomeAssistant_Repo`:

- Require a pull request before merging.
- Require the `Validate Home Assistant configuration` check.
- Require branches to be up to date.
- Block force pushes and deletion.
- Do not allow the app token to bypass branch protection.

## Options

- `repository`: private configuration repository in `owner/name` form.
- `branch`: protected inbound branch, normally `main`.
- `outbound_branch`: branch used for Home Assistant exports, normally `ha-sync`.
- `initial_source`: one-time bootstrap authority; `home_assistant` for an existing installation or `github` for a repository-led restore.
- `sync_interval`: polling period; minimum 30 seconds.
- `inbound_enabled`: apply validated protected-branch changes.
- `outbound_enabled`: export local changes to the PR branch.
- `auto_restart`: restart after a successful Supervisor config check.
- `backup_before_apply`: create a Supervisor partial backup before modifying files.
- `require_github_checks`: refuse commits without successful checks.
- `create_pull_request`: create one open PR for the outbound branch.
- `delete_removed`: delete a managed local path when it is absent from Git. Leave disabled until the setup is proven.
- `managed_paths`: explicit synchronization allowlist.
- `ignore_patterns`: additional non-sensitive exclusions.

## Recovery

If an inbound apply fails, the app restores its local rollback copy automatically. The log also records the Supervisor backup slug created before the attempt.

If Home Assistant still cannot start:

1. Start Home Assistant in safe mode.
2. Open **Settings → System → Backups**.
3. Restore the backup named `GitOps pre-apply ...`.
4. Revert the responsible GitHub commit before restarting the app.
