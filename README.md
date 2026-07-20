# Tomás's Home Assistant Custom Integrations

Central index for Home Assistant custom integrations and dashboard components maintained under [`Togarriapa`](https://github.com/Togarriapa).

Each installable project lives in its **own public repository** so HACS can install and update it independently. This collection provides one place to discover them and open the correct HACS installation link.

## HACS repositories

| Project | Type | Repository | HACS |
|---|---|---|---|
| Cast Metadata & TV Controls 8.4.0 | Integration | [`Togarriapa/HomeAssistant-Cast-Metadata-Controls`](https://github.com/Togarriapa/HomeAssistant-Cast-Metadata-Controls) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Cast-Metadata-Controls&category=integration) |
| Unified TV Card 1.4.0 | Dashboard | [`Togarriapa/HomeAssistant-Unified-TV-Card`](https://github.com/Togarriapa/HomeAssistant-Unified-TV-Card) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Unified-TV-Card&category=plugin) |

## Recommended installation order

1. Install or update **Cast Metadata & TV Controls**.
2. Restart Home Assistant and add/open the integration.
3. Under **Configure**, open **Configure physical device entities**.
4. For each TV, select every external `media_player`, `remote`, and restart `button` entity that belongs to that physical device.
5. Keep provider selection automatic unless several selected entities provide the same capability and the result is ambiguous.
6. Install or update **Unified TV Card**, hard-refresh the browser, and select the unified controller entity.

## V8 physical-device workflow

Cast Metadata & TV Controls 8.4.0 makes the configured physical-device inventory authoritative:

**Settings → Devices & services → Cast Metadata & TV Controls → Configure → Configure physical device entities**

Select all supported external entities that represent one real device. Generated entities owned by Cast Metadata & TV Controls, including the Controller entity, are excluded from setup and merge selectors.

The integration tracks external media players for explicit assignment while keeping automatic TV/Cast grouping conservative. Navigation, restart, application, input, power, volume, playback, seeking, and metadata providers are selected generically from the configured inventory, with manual overrides available for ambiguous installations.

Applications and physical inputs are discovered from the linked media-player entities, active application metadata, learned applications, and provider configuration.

Unified TV Card 1.4.0 consumes the 8.4 provider attributes and displays an explicit compatibility warning when the selected controller is running an older backend.

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

## Update recovery

The user's current HACS installations have remained pinned to old local copies despite newer GitHub releases. For this transition:

1. Open each repository directly in HACS.
2. Use **Redownload** and explicitly select integration `v8.4.0` and card `v1.4.0`.
3. Restart Home Assistant after installing the integration.
4. Hard-refresh the browser after installing the card:
   - macOS: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + F5`
5. Confirm the card diagnostics report backend `8.4.0` and card `1.4.0`.

Integration 8.4.0 is distributed as a verified HACS ZIP and card 1.4.0 as the exact validated JavaScript release asset.

## Machine-readable catalogue

`repositories.json` contains the same catalogue for scripts and future tooling.

## Adding a future project

1. Create a new public GitHub repository.
2. Follow the HACS structure for the relevant category.
3. Add validation, documentation, releases, and a license.
4. Add the project to `repositories.json` and this README.

## License

The collection metadata is licensed under the MIT License. Each project repository has its own license.
