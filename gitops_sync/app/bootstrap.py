from __future__ import annotations

import json
import time

from main import (
    DATA_DIR,
    LIVE_DIR,
    LOG,
    OPTIONS_FILE,
    REPO_DIR,
    ROLLBACK_DIR,
    Engine,
    Settings,
    SyncError,
    _save_state,
)

SUPPORTED_INITIAL_SOURCES = {"home_assistant", "github"}


class BootstrapEngine(Engine):
    """Engine with an explicit, one-time source-of-truth bootstrap."""

    def run_forever(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)
        self.git.prepare()
        LOG.info(
            "GitOps synchronization started for %s (%s)",
            self.settings.repository,
            self.settings.branch,
        )

        if not self.state.get("bootstrap_complete"):
            self.bootstrap()

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

    def bootstrap(self) -> None:
        raw_options = json.loads(OPTIONS_FILE.read_text(encoding="utf-8"))
        initial_source = str(
            raw_options.get("initial_source", "home_assistant")
        ).strip().lower()
        if initial_source not in SUPPORTED_INITIAL_SOURCES:
            raise SyncError(
                "initial_source must be either 'home_assistant' or 'github'"
            )

        remote_sha = self.git.checkout_remote(self.settings.branch)
        self._validate_repository()
        remote_has_managed_content = any(
            (REPO_DIR / managed).exists() for managed in self.settings.managed_paths
        )
        local_has_managed_content = any(
            (LIVE_DIR / managed).exists() for managed in self.settings.managed_paths
        )

        if initial_source == "home_assistant":
            if not self.settings.outbound_enabled:
                raise SyncError(
                    "Initial source is Home Assistant, but outbound synchronization is disabled"
                )
            if not local_has_managed_content:
                raise SyncError(
                    "Initial source is Home Assistant, but no managed local configuration exists"
                )

            if remote_has_managed_content:
                LOG.warning(
                    "The protected GitHub branch already contains managed configuration. "
                    "It will not be applied during bootstrap; the Home Assistant export will "
                    "be proposed on %s for review.",
                    self.settings.outbound_branch,
                )

            LOG.info(
                "Bootstrapping from the existing Home Assistant configuration into %s",
                self.settings.outbound_branch,
            )
            # Force a first export even if v0.1.0 previously cached the local hash.
            self.state.pop("last_local_hash", None)
            self.sync_outbound()
            self.state["last_remote_sha"] = remote_sha
            self.state["bootstrap_complete"] = True
            self.state["initial_source"] = initial_source
            _save_state(self.state)
            LOG.info(
                "Bootstrap export completed. Review and merge the GitHub pull request; "
                "the protected branch was not applied to Home Assistant."
            )
            return

        if not self.settings.inbound_enabled:
            raise SyncError(
                "Initial source is GitHub, but inbound synchronization is disabled"
            )
        if not remote_has_managed_content:
            raise SyncError(
                "Initial source is GitHub, but the protected branch contains no managed configuration"
            )

        LOG.warning(
            "Bootstrapping from GitHub. The validated protected branch will replace matching "
            "managed Home Assistant paths after backup and configuration checks."
        )
        # Force validation/application even if v0.1.0 cached the remote SHA.
        self.state.pop("last_remote_sha", None)
        self.sync_inbound()
        if self.state.get("last_remote_sha") != remote_sha:
            raise SyncError(
                "GitHub bootstrap was not applied. Confirm that required checks passed and retry."
            )
        self.state["bootstrap_complete"] = True
        self.state["initial_source"] = initial_source
        _save_state(self.state)
        LOG.info("GitHub bootstrap completed successfully")


def main() -> None:
    try:
        settings = Settings.load()
        BootstrapEngine(settings).run_forever()
    except Exception:
        LOG.exception("Fatal startup error")
        raise


if __name__ == "__main__":
    main()
