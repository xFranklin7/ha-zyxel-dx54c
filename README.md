# Zyxel Router integration for Home Assistant

A custom Home Assistant integration for reading connected Wi-Fi stations from Zyxel routers, starting with the Zyxel DX54C.

> **Development status:** early development. The DX54C login and WLAN station-table request have been verified with a standalone Python client. The Home Assistant integration is not yet ready for installation.

## Goals

- Local communication with the router; no cloud service.
- Configure router address and credentials through the Home Assistant UI.
- Discover associated Wi-Fi clients and expose presence plus available radio metrics.
- Keep credentials out of logs and diagnostics.
- Separate model-specific protocol handling so additional Zyxel models can be added later.
- Provide tests and documentation suitable for eventual HACS distribution.

## Initial target

- Router: Zyxel DX54C
- Station table endpoint: `GET /cgi-bin/WLANTable_handle`
- Bands: 2.4 GHz and 5 GHz
- Refresh target: 60 seconds initially

Wi-Fi association indicates that a client is connected to the access point. It does not provide room-level location or Bluetooth-style ranging.

## Installation

Not available yet. This repository is under active development; do not copy it into `custom_components` until a tested release is published.

## Security

Never publish router passwords, session cookies, AES session keys, exported browser storage, or unredacted diagnostic output. Report protocol problems with MAC addresses anonymized where possible.

## Development

The first milestone is to port the already verified DX54C authentication and WLAN-table parsing into an asynchronous Home Assistant client, then add config flow, coordinator, sensors, device trackers, and automated tests.

Contributions and reports for other Zyxel models are welcome, but support for a model will only be advertised after it has been tested.
