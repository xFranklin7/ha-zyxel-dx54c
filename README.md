# Zyxel Router integration for Home Assistant

[English](README.md) · [Italiano](README.it.md)

A local, read-only Home Assistant integration for discovering Wi-Fi clients connected to Zyxel routers. The first supported target is the **Zyxel DX54C**.

> **Development status: experimental.** The DX54C authentication exchange and WLAN station-table endpoint have been verified using a standalone Python client. The Home Assistant integration code is being developed and has not yet been validated against a live Home Assistant installation. Do not treat the current `main` branch as a stable release.

## Current implementation

- Local router communication; no cloud service.
- UI configuration with router address, username, and password.
- Asynchronous polling through Home Assistant's coordinator.
- Dynamic device trackers for discovered MAC addresses.
- Per-client sensors for RSSI, SNR, link rate, and signal level.
- Device names enriched from the router's read-only ARP table when available, matched by MAC address.
- Configurable polling interval (30–600 seconds; default 60).
- Diagnostics that omit passwords, session tokens, and client MAC addresses.

## Router protocol verified so far

- Authentication: `GET /getRSAPublickKey`, followed by encrypted `POST /UserLogin`.
- WLAN station table: plain `GET /cgi-bin/WLANTable_handle`, using the same HTTP session/cookies.
- The WLAN endpoint is read-only. No router configuration is changed.
- The table provides 2.4 GHz and 5 GHz client records, including MAC, link rate, RSSI, SNR, and signal level.
- A separate read-only `GET /cgi-bin/ARPTable_handle` provides IP/MAC/name records; names are joined to Wi-Fi clients by MAC. If the router has no name for a client or the ARP lookup fails, Wi-Fi tracking continues and the MAC-based fallback name is used.

## Presence limitations

A device tracker reports whether a MAC address is currently associated with the router's Wi-Fi. This is not Bluetooth ranging, room detection, or proof that a person is physically inside the home. Devices using randomized/private MAC addresses may appear as separate clients.

## Installation

There is no stable HACS release yet. Wait for a tagged release and installation instructions before adding this integration to a production Home Assistant instance.

For development, the integration directory is `custom_components/zyxel_dx54c`.

## Security and privacy

- Never commit router passwords, cookies, session keys, AES keys, or browser storage.
- Do not include unredacted client MAC addresses in public issue reports.
- The diagnostics endpoint intentionally reports counts by band instead of listing client identifiers.
- Use a unique, strong router administrator password.

## Development and tests

The parser tests are under `tests/`. The project will add Home Assistant config-flow and coordinator tests before the first release.

## Roadmap

1. Validate login and polling from Home Assistant against a real DX54C.
2. Add session-expiry recovery and robust firmware response handling.
3. Complete automated Home Assistant tests and CI.
4. Add support for other Zyxel models only after protocol verification.
5. Publish a tagged release and HACS installation guide.
