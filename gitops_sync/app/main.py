from __future__ import annotations

import fnmatch
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml

LOG = logging.getLogger("ha_gitops_sync")
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)

DATA_DIR = Path("/data")
LIVE_DIR = Path("/homeassistant")
REPO_DIR = DATA_DIR / "repository"
ROLLBACK_DIR = DATA_DIR / "rollbacks"
STATE_FILE = DATA_DIR / "state.json"
OPTIONS_FILE = DATA_DIR / "options.json"
TOKEN_FILE = DATA_DIR / "github-token"
ASKPASS_FILE = DATA_DIR / "git-askpass.sh"

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
HIGH_RISK_VALUE_RE = re.compile(
    r"(?im)^\s*(password|passwd|token|access_token|api_key|apikey|client_secret|secret)\s*:"
    r"\s*(?!$|!secret\b|!env_var\b|\{\{\s*secret\b)([\"']?[^#\s][^#\n]*)$"
)
HIGH_RISK_TOKEN_RE = re.compile(
    r"(github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
)

FORBIDDEN_PATTERNS = (
    "secrets.yaml",
    "**/secrets.yaml",
    ".storage/**",
    "home-assistant_v2.db*",
    "*.db-shm",
    "*.db-wal",
    "*.log*",
    "*.pem",
    "*.key",
    "known_devices.yaml",
    ".cloud/**",
    "backups/**",
)


class SyncError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    repository: str
    branch: str
    outbound_branch: str
    github_token: str
    sync_interval: int
    inbound_enabled: bool
    outbound_enabled: bool
    auto_restart: bool
    backup_before_apply: bool
    require_github_checks: bool
    create_pull_request: bool
    delete_removed: bool
    managed_paths: tuple[str, ...]
    ignore_patterns: tuple[str, ...]

    @classmethod
    def load(cls) -> "Settings":
        raw = json.loads(OPTIONS_FILE.read_text(encoding="utf-8"))
        repository = str(raw["repository"]).strip()
        if not REPOSITORY_RE.fullmatch(repository):
            raise SyncError("repository must use owner/name format")

        managed = tuple(_validate_relative_path(str(value)) for value in raw["managed_paths"])
        if not managed:
            raise SyncError("managed_paths cannot be empty")
        for path in managed:
            if _matches_any(path, FORBIDDEN_PATTERNS):
                raise SyncError(f"Unsafe managed path is forbidden: {path}")

        interval = int(raw.get("sync_interval", 60))
        if interval < 30:
            raise SyncError("sync_interval must be at least 30 seconds")

        return cls(
            repository=repository,
            branch=_validate_branch(str(raw.get("branch", "main")).strip()),
            outbound_branch=_validate_branch(
                str(raw.get("outbound_branch", "ha-sync")).strip()
            ),
            github_token=_validate_token(str(raw["github_token"]).strip()),
            sync_interval=interval,
            inbound_enabled=bool(raw.get("inbound_enabled", True)),
            outbound_enabled=bool(raw.get("outbound_enabled", True)),
            auto_restart=bool(raw.get("auto_restart", True)),
            backup_before_apply=bool(raw.get("backup_before_apply", True)),
            require_github_checks=bool(raw.get("require_github_checks", True)),
            create_pull_request=bool(raw.get("create_pull_request", True)),
            delete_removed=bool(raw.get("delete_removed", False)),
            managed_paths=managed,
            ignore_patterns=tuple(str(value) for value in raw.get("ignore_patterns", [])),
        )


def _validate_relative_path(value: str) -> str:
    value = value.strip().replace("\\", "/").rstrip("/")
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts or value.startswith(".git"):
        raise SyncError(f"Invalid relative path: {value!r}")
    return value


def _validate_branch(value: str) -> str:
    if (
        not value
        or value.startswith(("-", ".", "/"))
        or value.endswith((".", "/", ".lock"))
        or ".." in value
        or "@{" in value
        or any(character.isspace() or character in "~^:?*[\\" for character in value)
    ):
        raise SyncError(f"Invalid Git branch name: {value!r}")
    return value


def _validate_token(value: str) -> str:
    if not value:
        raise SyncError("github_token is required")
    return value


def _matches_any(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
    normalized = path.replace("\\", "/")
    return any(
        fnmatch.fnmatch(normalized, pattern)
        or fnmatch.fnmatch(normalized + "/", pattern)
        for pattern in patterns
    )


def _load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        LOG.warning("State file is invalid; starting with an empty state")
        return {}


def _save_state(state: dict[str, Any]) -> None:
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, STATE_FILE)


class Git:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        TOKEN_FILE.write_text(settings.github_token, encoding="utf-8")
        TOKEN_FILE.chmod(0o600)
        ASKPASS_FILE.write_text(
            "#!/bin/sh\n"
            'case "$1" in\n'
            '  *Username*) printf "%s\\n" "x-access-token" ;;\n'
            f'  *) cat "{TOKEN_FILE}" ;;\n'
            "esac\n",
            encoding="utf-8",
        )
        ASKPASS_FILE.chmod(0o700)
        self.environment = {
            **os.environ,
            "GIT_ASKPASS": str(ASKPASS_FILE),
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1",
        }

    @property
    def remote_url(self) -> str:
        return f"https://github.com/{self.settings.repository}.git"

    def run(
        self,
        *args: str,
        cwd: Path = REPO_DIR,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = ["git", *args]
        result = subprocess.run(
            command,
            cwd=cwd,
            env=self.environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and result.returncode:
            stderr = result.stderr.strip().replace(self.settings.github_token, "***")
            raise SyncError(f"git {' '.join(args)} failed: {stderr}")
        return result

    def prepare(self) -> None:
        if not (REPO_DIR / ".git").exists():
            if REPO_DIR.exists():
                shutil.rmtree(REPO_DIR)
            self.run("clone", "--no-checkout", self.remote_url, str(REPO_DIR), cwd=DATA_DIR)
        self.run("remote", "set-url", "origin", self.remote_url)
        self.run("config", "user.name", "Home Assistant GitOps Sync")
        self.run("config", "user.email", "home-assistant-gitops@users.noreply.github.com")
        self.run("fetch", "--prune", "origin")

    def remote_sha(self, branch: str) -> str | None:
        result = self.run("rev-parse", "--verify", f"origin/{branch}", check=False)
        return result.stdout.strip() if result.returncode == 0 else None

    def checkout_remote(self, branch: str) -> str:
        self.run("fetch", "--prune", "origin", branch)
        sha = self.remote_sha(branch)
        if not sha:
            raise SyncError(f"Remote branch does not exist: {branch}")
        self.run("checkout", "-B", branch, f"origin/{branch}")
        self.run("reset", "--hard", f"origin/{branch}")
        self.run("clean", "-fdx")
        return sha

    def prepare_outbound_branch(self) -> None:
        self.run("fetch", "--prune", "origin")
        remote_outbound = self.remote_sha(self.settings.outbound_branch)
        if remote_outbound:
            self.run(
                "checkout",
                "-B",
                self.settings.outbound_branch,
                f"origin/{self.settings.outbound_branch}",
            )
            result = self.run("rebase", f"origin/{self.settings.branch}", check=False)
            if result.returncode:
                self.run("rebase", "--abort", check=False)
                raise SyncError(
                    f"Outbound branch conflicts with {self.settings.branch}; resolve the PR manually"
                )
        else:
            self.run(
                "checkout",
                "-B",
                self.settings.outbound_branch,
                f"origin/{self.settings.branch}",
            )

    def commit_and_push(self, message: str) -> bool:
        self.run("add", "--all")
        if self.run("diff", "--cached", "--quiet", check=False).returncode == 0:
            return False
        self.run("commit", "-m", message)
        self.run(
            "push",
            "--force-with-lease",
            "--set-upstream",
            "origin",
            self.settings.outbound_branch,
        )
        return True


class GitHub:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "home-assistant-gitops-sync",
            }
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        response = self.session.request(
            method,
            f"https://api.github.com{path}",
            timeout=30,
            **kwargs,
        )
        if response.status_code >= 400:
            raise SyncError(
                f"GitHub API {method} {path} failed with HTTP {response.status_code}"
            )
        return response

    def checks_passed(self, sha: str) -> bool:
        checks = self._request(
            "GET",
            f"/repos/{self.settings.repository}/commits/{sha}/check-runs",
        ).json().get("check_runs", [])
        statuses = self._request(
            "GET",
            f"/repos/{self.settings.repository}/commits/{sha}/status",
        ).json()

        if checks:
            allowed = {"success", "neutral", "skipped"}
            if any(
                check.get("status") != "completed"
                or check.get("conclusion") not in allowed
                for check in checks
            ):
                return False

        status_count = int(statuses.get("total_count", 0))
        if status_count and statuses.get("state") != "success":
            return False

        return bool(checks or status_count)

    def ensure_pull_request(self) -> None:
        owner = self.settings.repository.split("/", 1)[0]
        params = {
            "state": "open",
            "head": f"{owner}:{self.settings.outbound_branch}",
            "base": self.settings.branch,
        }
        pulls = self._request(
            "GET",
            f"/repos/{self.settings.repository}/pulls",
            params=params,
        ).json()
        if pulls:
            return
        self._request(
            "POST",
            f"/repos/{self.settings.repository}/pulls",
            json={
                "title": "Synchronize Home Assistant configuration",
                "head": self.settings.outbound_branch,
                "base": self.settings.branch,
                "body": (
                    "Automated configuration export from Home Assistant. "
                    "Merge only after all validation checks pass."
                ),
                "draft": False,
            },
        )
        LOG.info("Created synchronization pull request")


class Supervisor:
    def __init__(self) -> None:
        token = os.environ.get("SUPERVISOR_TOKEN")
        if not token:
            raise SyncError("SUPERVISOR_TOKEN is unavailable")
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: int = 120,
        accepted: tuple[int, ...] = (200,),
        **kwargs: Any,
    ) -> requests.Response:
        response = self.session.request(
            method,
            f"http://supervisor{path}",
            timeout=timeout,
            **kwargs,
        )
        if response.status_code not in accepted:
            raise SyncError(
                f"Supervisor {method} {path} failed with HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )
        return response

    def core_version(self) -> str:
        payload = self._request("GET", "/core/info").json()
        return str(payload.get("data", payload).get("version", "stable"))

    def create_backup(self) -> str | None:
        payload = {
            "name": f"GitOps pre-apply {datetime.now(timezone.utc).isoformat()}",
            "homeassistant": True,
            "homeassistant_exclude_database": True,
            "background": False,
        }
        response = self._request(
            "POST",
            "/backups/new/partial",
            timeout=900,
            json=payload,
        ).json()
        data = response.get("data", response)
        return data.get("slug")

    def check_config(self) -> None:
        response = self._request("POST", "/core/check", timeout=300).json()
        data = response.get("data", response)
        if isinstance(data, dict) and data.get("result") == "error":
            raise SyncError(f"Home Assistant configuration check failed: {data.get('errors')}")
        if response.get("result") == "error":
            raise SyncError(f"Home Assistant configuration check failed: {response}")

    def restart(self, *, safe_mode: bool = False) -> None:
        self._request(
            "POST",
            "/core/restart",
            timeout=120,
            accepted=(200, 201),
            json={"safe_mode": safe_mode},
        )

    def wait_until_healthy(self, timeout: int = 300) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                response = self._request(
                    "GET",
                    "/core/api/config",
                    timeout=15,
                    accepted=(200,),
                )
                if response.ok:
                    return True
            except (requests.RequestException, SyncError):
                pass
            time.sleep(5)
        return False


class Engine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.git = Git(settings)
        self.github = GitHub(settings)
        self.supervisor = Supervisor()
        self.state = _load_state()

    def run_forever(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)
        self.git.prepare()
        LOG.info(
            "GitOps synchronization started for %s (%s)",
            self.settings.repository,
            self.settings.branch,
        )
        while True:
            cycle_started = time.monotonic()
            try:
                if self.settings.inbound_enabled:
                    self.sync_inbound()
                if self.settings.outbound_enabled:
                    self.sync_outbound()
            except Exception:
                LOG.exception("Synchronization cycle failed")
            elapsed = time.monotonic() - cycle_started
            time.sleep(max(5, self.settings.sync_interval - elapsed))

    def sync_inbound(self) -> None:
        self.git.run("fetch", "--prune", "origin", self.settings.branch)
        remote_sha = self.git.remote_sha(self.settings.branch)
        if not remote_sha or remote_sha == self.state.get("last_remote_sha"):
            return

        if self.settings.require_github_checks and not self.github.checks_passed(remote_sha):
            LOG.warning("Remote commit %s is not fully validated; refusing to apply", remote_sha)
            return

        LOG.info("Validating inbound commit %s", remote_sha)
        self.git.checkout_remote(self.settings.branch)
        self._validate_repository()

        if not self._would_change_live():
            self.state["last_remote_sha"] = remote_sha
            self.state["last_local_hash"] = self._local_hash()
            _save_state(self.state)
            LOG.info("Inbound commit %s contains no effective managed changes", remote_sha)
            return

        backup_slug = None
        if self.settings.backup_before_apply:
            backup_slug = self.supervisor.create_backup()
            LOG.info("Created Supervisor backup %s", backup_slug or "<unknown>")

        rollback = self._create_file_rollback(remote_sha)
        try:
            self._apply_managed_paths()
            self.supervisor.check_config()
            if self.settings.auto_restart:
                self.supervisor.restart()
                if not self.supervisor.wait_until_healthy():
                    raise SyncError("Home Assistant did not become healthy after restart")
        except Exception:
            LOG.exception("Inbound apply failed; restoring previous configuration")
            self._restore_file_rollback(rollback)
            try:
                self.supervisor.restart()
                if not self.supervisor.wait_until_healthy():
                    LOG.critical(
                        "Rollback files were restored but Home Assistant is still unhealthy; "
                        "start it in safe mode and restore Supervisor backup %s",
                        backup_slug,
                    )
            except Exception:
                LOG.exception("Could not restart Home Assistant after file rollback")
            raise

        self.state["last_remote_sha"] = remote_sha
        self.state["last_local_hash"] = self._local_hash()
        self.state["last_backup_slug"] = backup_slug
        _save_state(self.state)
        LOG.info("Inbound commit %s applied successfully", remote_sha)

    def sync_outbound(self) -> None:
        current_hash = self._local_hash()
        if current_hash == self.state.get("last_local_hash"):
            return

        LOG.info("Local Home Assistant configuration changed; preparing export")
        self.git.prepare_outbound_branch()
        self._export_managed_paths()
        version = self.supervisor.core_version()
        (REPO_DIR / ".ha-version").write_text(version + "\n", encoding="utf-8")
        self._validate_repository()

        committed = self.git.commit_and_push(
            f"Synchronize Home Assistant configuration ({datetime.now(timezone.utc).isoformat()})"
        )
        if committed and self.settings.create_pull_request:
            self.github.ensure_pull_request()

        self.state["last_local_hash"] = current_hash
        _save_state(self.state)
        LOG.info("Local configuration synchronized to branch %s", self.settings.outbound_branch)

    def _iter_managed_files(self, root: Path):
        for managed in self.settings.managed_paths:
            candidate = root / managed
            if not candidate.exists():
                continue
            if candidate.is_symlink():
                raise SyncError(f"Symlink is forbidden: {managed}")
            if candidate.is_file():
                relative = candidate.relative_to(root).as_posix()
                if not self._ignored(relative):
                    yield candidate, relative
                continue
            for path in sorted(candidate.rglob("*")):
                if path.is_symlink():
                    raise SyncError(f"Symlink is forbidden: {path.relative_to(root)}")
                if not path.is_file():
                    continue
                relative = path.relative_to(root).as_posix()
                if not self._ignored(relative):
                    yield path, relative

    def _ignored(self, relative: str) -> bool:
        return _matches_any(
            relative,
            list(FORBIDDEN_PATTERNS) + list(self.settings.ignore_patterns),
        )

    def _validate_repository(self) -> None:
        for managed in self.settings.managed_paths:
            candidate = REPO_DIR / managed
            if not candidate.exists():
                continue
            paths = [candidate] if candidate.is_file() or candidate.is_symlink() else candidate.rglob("*")
            for path in paths:
                if path.is_symlink():
                    raise SyncError(f"Symlink is forbidden: {path.relative_to(REPO_DIR)}")
                if not path.is_file():
                    continue
                relative = path.relative_to(REPO_DIR).as_posix()
                if _matches_any(relative, FORBIDDEN_PATTERNS):
                    raise SyncError(f"Forbidden path is present in repository: {relative}")
                if _matches_any(relative, self.settings.ignore_patterns):
                    continue
                if path.stat().st_size > 10 * 1024 * 1024:
                    raise SyncError(f"Managed file exceeds 10 MiB: {relative}")
                data = path.read_bytes()
                if b"\x00" in data:
                    raise SyncError(f"Binary managed file is forbidden: {relative}")
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError as err:
                    raise SyncError(f"Non-UTF-8 managed file is forbidden: {relative}") from err
                if HIGH_RISK_TOKEN_RE.search(text) or HIGH_RISK_VALUE_RE.search(text):
                    raise SyncError(
                        f"Possible plaintext credential detected in {relative}; use !secret"
                    )
                if path.suffix.lower() in {".yaml", ".yml"}:
                    try:
                        list(yaml.compose_all(text))
                    except yaml.YAMLError as err:
                        raise SyncError(f"Invalid YAML in {relative}: {err}") from err

    def _would_change_live(self) -> bool:
        for managed in self.settings.managed_paths:
            source = REPO_DIR / managed
            destination = LIVE_DIR / managed
            if source.exists():
                if not destination.exists():
                    return True
                if source.is_file() != destination.is_file():
                    return True
                if source.is_file():
                    if source.read_bytes() != destination.read_bytes():
                        return True
                elif self._tree_hash(source, REPO_DIR) != self._tree_hash(
                    destination, LIVE_DIR
                ):
                    return True
            elif self.settings.delete_removed and destination.exists():
                return True
        return False

    def _tree_hash(self, root: Path, base: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                raise SyncError(f"Symlink is forbidden: {path.relative_to(base)}")
            if not path.is_file():
                continue
            relative = path.relative_to(base).as_posix()
            if self._ignored(relative):
                continue
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
        return digest.hexdigest()

    def _local_hash(self) -> str:
        digest = hashlib.sha256()
        for path, relative in self._iter_managed_files(LIVE_DIR):
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        return digest.hexdigest()

    def _create_file_rollback(self, remote_sha: str) -> Path:
        target = ROLLBACK_DIR / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + remote_sha[:12]
        )
        target.mkdir(parents=True, exist_ok=False)
        for managed in self.settings.managed_paths:
            source = LIVE_DIR / managed
            destination = target / managed
            if source.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(source, destination, symlinks=False)
                else:
                    shutil.copy2(source, destination)
        (target / ".manifest.json").write_text(
            json.dumps({"managed_paths": self.settings.managed_paths}, indent=2),
            encoding="utf-8",
        )
        self._prune_rollbacks()
        return target

    def _restore_file_rollback(self, rollback: Path) -> None:
        for managed in self.settings.managed_paths:
            destination = LIVE_DIR / managed
            source = rollback / managed
            if destination.exists():
                if destination.is_dir():
                    shutil.rmtree(destination)
                else:
                    destination.unlink()
            if source.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(source, destination, symlinks=False)
                else:
                    shutil.copy2(source, destination)

    def _apply_managed_paths(self) -> None:
        for managed in self.settings.managed_paths:
            source = REPO_DIR / managed
            destination = LIVE_DIR / managed
            if source.exists():
                temporary = destination.with_name(destination.name + ".gitops-new")
                previous = destination.with_name(destination.name + ".gitops-old")
                for stale in (temporary, previous):
                    if stale.exists():
                        if stale.is_dir():
                            shutil.rmtree(stale)
                        else:
                            stale.unlink()
                temporary.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(source, temporary, symlinks=False)
                else:
                    shutil.copy2(source, temporary)

                if destination.exists():
                    os.replace(destination, previous)
                try:
                    os.replace(temporary, destination)
                except Exception:
                    if previous.exists() and not destination.exists():
                        os.replace(previous, destination)
                    raise
                if previous.exists():
                    if previous.is_dir():
                        shutil.rmtree(previous)
                    else:
                        previous.unlink()
            elif self.settings.delete_removed and destination.exists():
                if destination.is_dir():
                    shutil.rmtree(destination)
                else:
                    destination.unlink()

    def _export_managed_paths(self) -> None:
        for managed in self.settings.managed_paths:
            destination = REPO_DIR / managed
            if destination.exists():
                if destination.is_dir():
                    shutil.rmtree(destination)
                else:
                    destination.unlink()

        for source, relative in self._iter_managed_files(LIVE_DIR):
            destination = REPO_DIR / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def _prune_rollbacks(self) -> None:
        directories = sorted(
            (path for path in ROLLBACK_DIR.iterdir() if path.is_dir()),
            key=lambda path: path.name,
            reverse=True,
        )
        for old in directories[5:]:
            shutil.rmtree(old, ignore_errors=True)


def main() -> None:
    try:
        settings = Settings.load()
        Engine(settings).run_forever()
    except Exception:
        LOG.exception("Fatal startup error")
        raise


if __name__ == "__main__":
    main()
