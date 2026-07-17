# Tomás's Home Assistant Custom Integrations

Central index for Home Assistant custom integrations and dashboard components maintained under [`Togarriapa`](https://github.com/Togarriapa).

Each installable project lives in its **own public repository** so HACS can install and update it independently. This collection provides one place to discover them and open the correct HACS installation link.

## HACS repositories

| Project | Type | Repository | HACS |
|---|---|---|---|
| Cast Metadata & TV Controls 8.0.0 | Integration | [`Togarriapa/HomeAssistant-Cast-Metadata-Controls`](https://github.com/Togarriapa/HomeAssistant-Cast-Metadata-Controls) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Cast-Metadata-Controls&category=integration) |
| Unified TV Card 1.2.0 | Dashboard | [`Togarriapa/HomeAssistant-Unified-TV-Card`](https://github.com/Togarriapa/HomeAssistant-Unified-TV-Card) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Unified-TV-Card&category=plugin) |

## Recommended installation order

1. Install **Cast Metadata & TV Controls**.
2. Restart Home Assistant and add the integration.
3. Open **Settings → Devices & services → Cast Metadata & TV Controls → Configure**.
4. Use **Review detected physical devices** to inspect automatic grouping.
5. When two entries represent the same television, use **Merge duplicate physical devices**, select both generated controller devices, and save.
6. Install **Unified TV Card**.
7. Add the card to a dashboard and select the surviving unified controller entity.

## HACS update tracking

HACS tracks each repository independently. Version 8 uses a full GitHub release and supports Home Assistant 2025.12 or newer. If an update does not immediately appear, reload HACS data or restart Home Assistant; do not add the repository a second time.

The collection repository is only a catalogue. Updates come from the individual integration and dashboard repositories.

## Hybrid repository structure

```text
HomeAssistant-Custom-Integrations       ← collection and catalogue
HomeAssistant-Cast-Metadata-Controls    ← HACS integration repository
HomeAssistant-Unified-TV-Card           ← HACS dashboard repository
HomeAssistant-Another-Integration       ← future repository
...
```

Integration repositories contain one directory under `custom_components/`; dashboard repositories contain their installable JavaScript bundle.

HACS does not bulk-import an arbitrary third-party collection. Add each repository once through its **Open in HACS** link, after which HACS tracks updates separately.

## Machine-readable catalogue

`repositories.json` contains the same catalogue for scripts and future tooling.

## Adding a future project

1. Create a new public GitHub repository.
2. Follow the HACS structure for the relevant category.
3. Add validation, documentation, releases, and a license.
4. Add the project to `repositories.json` and this README.

## License

The collection metadata is licensed under the MIT License. Each project repository has its own license.
