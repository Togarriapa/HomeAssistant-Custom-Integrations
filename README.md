# Tomás's Home Assistant Custom Integrations

Central index for Home Assistant custom integrations and dashboard components maintained under [`Togarriapa`](https://github.com/Togarriapa).

Each installable project lives in its **own public repository** so HACS can install and update it independently. This collection provides one place to discover them and open the correct HACS installation link.

## HACS repositories

| Project | Type | Repository | HACS |
|---|---|---|---|
| Cast Metadata & TV Controls 8.3.2 | Integration | [`Togarriapa/HomeAssistant-Cast-Metadata-Controls`](https://github.com/Togarriapa/HomeAssistant-Cast-Metadata-Controls) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Cast-Metadata-Controls&category=integration) |
| Unified TV Card 1.3.2 | Dashboard | [`Togarriapa/HomeAssistant-Unified-TV-Card`](https://github.com/Togarriapa/HomeAssistant-Unified-TV-Card) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Unified-TV-Card&category=plugin) |

## Recommended installation order

1. Install or update **Cast Metadata & TV Controls**.
2. Restart Home Assistant and add/open the integration.
3. Under **Configure**, open **Configure physical device entities**.
4. For each TV, select every `media_player`, `remote`, and restart `button` entity that belongs to that physical device.
5. Keep provider selection automatic unless several selected entities provide the same capability and the result is ambiguous.
6. Install or update **Unified TV Card**, hard-refresh the browser, and select the unified controller entity.

## V8 physical-device workflow

Cast Metadata & TV Controls 8.3.2 makes the configured physical-device inventory authoritative:

**Settings → Devices & services → Cast Metadata & TV Controls → Configure → Configure physical device entities**

Select all supported entities that represent one real device. The integration creates or updates its persistent physical group and chooses the best provider for each capability from that inventory. It consolidates the controller device owned by this integration; native devices owned by other Home Assistant integrations remain separate registry records.

Navigation and restart providers are selected generically using entity domain, availability, device association, config entry, area, device class, and name evidence. **Override entity providers** remains available for ambiguous installations.

Applications and physical inputs are discovered from the selected media-player entities. Version 8.3.2 preserves the 8.3 runtime corrections while using a clean semantic-version transition and verified HACS release ZIP.

Unified TV Card 1.3.2 preserves the rebuilt generic provider/application handling and publishes the exact validated JavaScript as a verified latest release asset.

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

1. Open the relevant repository in HACS and select **Update information**.
2. Install the offered update normally.
3. Restart Home Assistant after the integration update.
4. Hard-refresh the browser once after the card update:
   - macOS: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + F5`

Integration 8.3.2 is distributed as a verified HACS ZIP and card 1.3.2 as the exact verified JavaScript release asset.

## Machine-readable catalogue

`repositories.json` contains the same catalogue for scripts and future tooling.

## Adding a future project

1. Create a new public GitHub repository.
2. Follow the HACS structure for the relevant category.
3. Add validation, documentation, releases, and a license.
4. Add the project to `repositories.json` and this README.

## License

The collection metadata is licensed under the MIT License. Each project repository has its own license.
