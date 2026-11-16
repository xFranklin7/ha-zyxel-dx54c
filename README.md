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
- Configurable polling interval (15–600 seconds; default 60).
- Diagnostics that omit passwords, session tokens, and client MAC addresses.

## Device names

**Device names must be assigned manually in Home Assistant.** The integration discovers Wi-Fi clients and identifies them by MAC address, but the ARP table on the tested DX54C firmware does not provide usable hostnames. Therefore, the integration cannot automatically determine descriptive names such as “iPhone”, “Living room TV”, or “Laptop”.

After a device has been discovered:

1. Open **Settings → Devices & services → Devices** in Home Assistant.
2. Select the device created by the Zyxel integration.
3. Open the device settings and change its name to a recognizable label.

The name assigned in Home Assistant makes the device easier to identify in dashboards and automations. If a device uses a private or randomized MAC address, you may need to rename it again when it appears with a different MAC.

## Router protocol verified so far

- Authentication: `GET /getRSAPublickKey`, followed by encrypted `POST /UserLogin`.
- WLAN station table: plain `GET /cgi-bin/WLANTable_handle`, using the same HTTP session/cookies.
- The WLAN endpoint is read-only. No router configuration is changed.
- The table provides 2.4 GHz and 5 GHz client records, including MAC, link rate, RSSI, SNR, and signal level.

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
