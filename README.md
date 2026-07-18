# Tomás's Home Assistant Custom Integrations

Central index for Home Assistant custom integrations and dashboard components maintained under [`Togarriapa`](https://github.com/Togarriapa).

Each installable project lives in its **own public repository** so HACS can install and update it independently. This collection provides one place to discover them and open the correct HACS installation link.

## HACS repositories

| Project | Type | Repository | HACS |
|---|---|---|---|
| Cast Metadata & TV Controls 8.3.0 | Integration | [`Togarriapa/HomeAssistant-Cast-Metadata-Controls`](https://github.com/Togarriapa/HomeAssistant-Cast-Metadata-Controls) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Cast-Metadata-Controls&category=integration) |
| Unified TV Card 1.3.0 | Dashboard | [`Togarriapa/HomeAssistant-Unified-TV-Card`](https://github.com/Togarriapa/HomeAssistant-Unified-TV-Card) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Unified-TV-Card&category=plugin) |

## Recommended installation order

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

## Hybrid repository structure

```text
HomeAssistant-Custom-Integrations       ← collection and catalogue
HomeAssistant-Cast-Metadata-Controls    ← HACS integration repository
HomeAssistant-Unified-TV-Card           ← HACS dashboard repository
HomeAssistant-Another-Integration       ← future repository
...
```

HACS manages each repository independently. Integration repositories contain one directory under `custom_components/`; dashboard repositories contain their installable JavaScript bundle.

HACS does not bulk-import an arbitrary third-party collection. Add each repository once through its **Open in HACS** link, after which HACS tracks updates separately.

## Update troubleshooting

If an update does not appear:

1. Open the relevant repository in HACS and select **Update information**.
2. Confirm it was added under the correct category: Integration or Dashboard.
3. Use **Redownload** when local HACS metadata is stale.
4. Restart Home Assistant after integration updates.
5. Hard-refresh the browser after dashboard-card updates:
   - macOS: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + F5`

Backend 8.3.0 and card 1.3.0 use matching source metadata, tags, and full latest GitHub releases so HACS can discover their updates independently.

## Machine-readable catalogue

`repositories.json` contains the same catalogue for scripts and future tooling.

## Adding a future project

1. Create a new public GitHub repository.
2. Follow the HACS structure for the relevant category.
3. Add validation, documentation, releases, and a license.
4. Add the project to `repositories.json` and this README.

## License

The collection metadata is licensed under the MIT License. Each project repository has its own license.
