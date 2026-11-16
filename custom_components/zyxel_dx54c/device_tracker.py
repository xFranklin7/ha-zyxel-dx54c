"""Track Wi-Fi association for clients seen by the router."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.device_tracker import ScannerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import ZyxelDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: ZyxelDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    @callback
    def add_new_clients() -> None:
        new_macs = [mac for mac in coordinator.known_stations if mac not in added]
        if new_macs:
            async_add_entities([ZyxelDeviceTracker(coordinator, mac) for mac in new_macs])
            added.update(new_macs)

    add_new_clients()
    entry.async_on_unload(coordinator.async_add_listener(add_new_clients))


class ZyxelDeviceTracker(CoordinatorEntity, ScannerEntity):
    """Presence of one MAC address on the wireless access point."""

    _attr_has_entity_name = True
    _attr_name = "Presence"
    _attr_icon = "mdi:wifi"
    # ScannerEntity is disabled by default in Home Assistant 2026.11.
    _attr_entity_registry_enabled_default = True
    _consider_home = timedelta(seconds=90)

    def __init__(self, coordinator: ZyxelDataUpdateCoordinator, mac: str) -> None:
        super().__init__(coordinator)
        self.mac = mac
        self._last_seen = None
        self._attr_unique_id = f"{mac.replace(':', '').lower()}_presence"
    @property
    def device_info(self):
        """Expose the router-reported host name when one is available."""
        station = self.coordinator.known_stations.get(self.mac, {})
        return {
            "identifiers": {(DOMAIN, self.mac)},
            "name": station.get("name") or f"Wi-Fi client {self.mac}",
            "manufacturer": "Zyxel",
            "model": "DX54C Wi-Fi client",
        }

    @property
    def is_connected(self) -> bool:
        if self.mac in (self.coordinator.data or {}):
            self._last_seen = dt_util.utcnow()
        return self._last_seen is not None and dt_util.utcnow() - self._last_seen < self._consider_home

    @property
    def mac_address(self) -> str:
        return self.mac

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose both the hardware address and router-reported host name."""
        station = self.coordinator.known_stations.get(self.mac, {})
        attributes = {"mac": self.mac}
        if station.get("name"):
            attributes["device_name"] = station["name"]
        return attributes
