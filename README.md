# Tomás's Home Assistant Projects

Central catalogue for Home Assistant integrations, dashboard components, and supervised apps maintained under [`Togarriapa`](https://github.com/Togarriapa).

HACS integrations and dashboard components live in independent public repositories so they can be installed and updated separately. Supervised apps can be published directly from this repository through its root `repository.yaml`.

## HACS repositories

| Project | Type | Repository | HACS |
|---|---|---|---|
| Cast Metadata & TV Controls 8.3.0 | Integration | [`Togarriapa/HomeAssistant-Cast-Metadata-Controls`](https://github.com/Togarriapa/HomeAssistant-Cast-Metadata-Controls) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Cast-Metadata-Controls&category=integration) |
| Unified TV Card 1.3.0 | Dashboard | [`Togarriapa/HomeAssistant-Unified-TV-Card`](https://github.com/Togarriapa/HomeAssistant-Unified-TV-Card) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Unified-TV-Card&category=plugin) |

## Home Assistant apps

### Home Assistant GitOps Sync 0.1.0

A supervised app that synchronizes declarative Home Assistant configuration with a private GitHub repository using a protected-branch and pull-request workflow.

Safety controls include:

- explicit path allowlisting and sensitive-file blocking;
- GitHub status/check gating before inbound deployment;
- exact Home Assistant version pinning for CI validation;
- Supervisor backup and separate file rollback before changes;
- Supervisor configuration validation before restart;
- authenticated post-restart health checks and automatic rollback;
- local Home Assistant edits exported only to a dedicated PR branch.

Install the app repository by adding:

`https://github.com/Togarriapa/HomeAssistant-Custom-Integrations`

See [`gitops_sync/DOCS.md`](gitops_sync/DOCS.md) before installation.

## Recommended TV installation order

1. Install or update **Cast Metadata & TV Controls**.
2. Restart Home Assistant and add/open the integration.
3. Under **Configure**, open **Configure physical device entities**.
4. For each TV, select every `media_player`, `remote`, and restart `button` entity that belongs to that physical device.
5. Keep provider selection automatic unless several selected entities provide the same capability and the result is ambiguous.
6. Install or update **Unified TV Card**, hard-refresh the browser, and select the unified controller entity.

## V8 physical-device workflow

Cast Metadata & TV Controls 8.3.0 makes the configured physical-device inventory authoritative:

**Settings → Devices & services → Cast Metadata & TV Controls → Configure → Configure physical device entities**

Select all supported entities that represent one real device. The integration creates or updates the persistent physical group and then chooses the best provider for each capability from that inventory.

Navigation and restart providers are selected generically using entity domain, availability, device association, config entry, area, device class, and name evidence. **Override entity providers** is available only for ambiguous installations.

Remote buttons use logical commands such as `HOME`, `BACK`, `SETTINGS`, and `DPAD_CENTER`. When a remote provider expects different values, configure them under **Configure remote commands**. Provider-specific commands remain configuration data rather than hardcoded manufacturer profiles.

Applications and physical inputs are discovered from the selected media-player entities. Native and Cast versions of the same service remain separate routes.

Unified TV Card 1.3.0 consumes the backend's `remote_available` capability, resolves relative Home Assistant artwork URLs, searches all grouped source entities for artwork, and reports actual service failures.

## Repository structure

```text
HomeAssistant-Custom-Integrations       ← catalogue and Home Assistant app repository
└── gitops_sync                         ← supervised GitOps Sync app
HomeAssistant-Cast-Metadata-Controls    ← HACS integration repository
HomeAssistant-Unified-TV-Card           ← HACS dashboard repository
HomeAssistant_Repo                      ← private protected configuration repository
```

HACS manages each HACS repository independently. Home Assistant's app store reads `repository.yaml` and the app directory from this repository.

## Update troubleshooting

If a HACS update does not appear:

1. Open the relevant repository in HACS and select **Update information**.
2. Confirm it was added under the correct category: Integration or Dashboard.
3. Use **Redownload** when local HACS metadata is stale.
4. Restart Home Assistant after integration updates.
5. Hard-refresh the browser after dashboard-card updates:
   - macOS: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + F5`

## Machine-readable catalogue

`repositories.json` contains the HACS catalogue for scripts and future tooling.

## License

The collection metadata and GitOps Sync app are licensed under the MIT License. Each independent project repository has its own license.
