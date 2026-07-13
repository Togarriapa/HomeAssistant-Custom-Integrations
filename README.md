# Tomás's Home Assistant Custom Integrations

Central index for Home Assistant custom integrations maintained under the GitHub account [`Togarriapa`](https://github.com/Togarriapa).

Each integration lives in its **own public repository** so HACS can install and update it independently. This collection repository provides one place to discover them, review their status, and open the correct HACS installation link.

## Integrations

| Integration | Domain | Repository | HACS |
|---|---|---|---|
| Cast Metadata & TV Controls | `cast_attribute_sensors` | [`Togarriapa/HomeAssistant-Cast-Metadata-Controls`](https://github.com/Togarriapa/HomeAssistant-Cast-Metadata-Controls) | [Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=Togarriapa&repository=HomeAssistant-Cast-Metadata-Controls&category=integration) |

## How the hybrid structure works

```text
HomeAssistant-Custom-Integrations       ← collection, catalogue and documentation
HomeAssistant-Cast-Metadata-Controls    ← one HACS integration repository
HomeAssistant-Another-Integration       ← one future HACS integration repository
...
```

HACS requires each integration repository to contain only one directory under `custom_components/`. For that reason this collection is an index, not a monorepo containing all integration code.

HACS does not currently bulk-import an arbitrary third-party collection. Add each repository once using its **Open in HACS** link. After installation, HACS tracks updates for every integration separately.

## Adding a future integration

1. Create a new public GitHub repository.
2. Keep exactly one integration under:

   ```text
   custom_components/<integration_domain>/
   ```

3. Add `hacs.json`, documentation, an issue tracker, and a versioned `manifest.json`.
4. Add the repository to `repositories.json` in this collection.
5. Add a new row and one-click HACS link to this README.

## Machine-readable catalogue

`repositories.json` contains the same list in a simple machine-readable format for scripts or future tooling.

## License

The collection metadata is licensed under the MIT License. Each integration repository has its own license file.
