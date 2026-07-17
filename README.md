# Tomás's Home Assistant Custom Integrations

Central index for Home Assistant custom integrations and dashboard components maintained under [`Togarriapa`](https://github.com/Togarriapa).

Each installable project lives in its **own public repository** so HACS can install and update it independently. This collection provides one place to discover them and open the correct HACS installation link.

## HACS repositories

| Project | Type | Repository | HACS |
|---|---|---|---|
| Cast Metadata & TV Controls 8.0.0 | Integration | [`Togarriapa/HomeAssistant-Cast-Metadata-Controls`](https://github.com/Togarriapa/HomeAssistant-Cast-Metadata-Controls) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Cast-Metadata-Controls&category=integration) |
| Unified TV Card 1.2.1 | Dashboard | [`Togarriapa/HomeAssistant-Unified-TV-Card`](https://github.com/Togarriapa/HomeAssistant-Unified-TV-Card) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Unified-TV-Card&category=plugin) |

## Recommended installation order

1. Install or update **Cast Metadata & TV Controls**.
2. Restart Home Assistant and add/open the integration.
3. Under **Configure**, review the detected physical devices and merge any duplicate controller devices.
4. Install or update **Unified TV Card**.
5. Add the card to a dashboard and select the surviving unified controller entity.

## V8 duplicate-device workflow

Cast Metadata & TV Controls V8 adds a first-class configuration wizard:

**Settings → Devices & services → Cast Metadata & TV Controls → Configure → Merge duplicate physical devices**

Select the duplicate controller devices that represent the same TV. The integration expands them into their native BRAVIA, MediaRenderer, Android TV Remote, ADB, Cast, and manufacturer entities, migrates their settings, reloads, and cleans the obsolete generated device.

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
4. Restart Home Assistant after integration updates and hard-refresh the browser after dashboard-card updates.

The backend V8 release lowers its accidental Home Assistant 2026.7 compatibility floor to 2025.12 and publishes a verified full GitHub release, allowing HACS to expose the update on compatible installations. The card 1.2.1 release uses the same self-healing full-release approach.

## Machine-readable catalogue

`repositories.json` contains the same catalogue for scripts and future tooling.

## Adding a future project

1. Create a new public GitHub repository.
2. Follow the HACS structure for the relevant category.
3. Add validation, documentation, releases, and a license.
4. Add the project to `repositories.json` and this README.

## License

The collection metadata is licensed under the MIT License. Each project repository has its own license.
