"""Signal and link sensors for connected Wi-Fi clients."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass

from .const import DOMAIN
from .coordinator import ZyxelDataUpdateCoordinator

SENSORS = (
    ("rssi", "RSSI", "dBm"),
    ("snr", "SNR", "dB"),
    ("rate_mbps", "Link rate", "Mbit/s"),
    ("level", "Signal level", None),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: ZyxelDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    @callback
    def add_new_clients() -> None:
        new_macs = [mac for mac in coordinator.known_stations if mac not in added]
        if new_macs:
            async_add_entities([
                ZyxelClientSensor(coordinator, mac, key, name, unit)
                for mac in new_macs
                for key, name, unit in SENSORS
            ])
            added.update(new_macs)

    add_new_clients()
    entry.async_on_unload(coordinator.async_add_listener(add_new_clients))


class ZyxelClientSensor(CoordinatorEntity, SensorEntity):
    """One metric belonging to a router client."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, mac: str, key: str, name: str, unit: str | None) -> None:
        super().__init__(coordinator)
        self.mac = mac
        self.key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{mac.replace(':', '').lower()}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, mac)},
            "name": f"Wi-Fi client {mac}",
            "manufacturer": "Zyxel",
            "model": "DX54C Wi-Fi client",
        }

    @property
    def native_value(self):
        station = (self.coordinator.data or {}).get(self.mac)
        return station.get(self.key) if station else None

    @property
    def extra_state_attributes(self):
        station = (self.coordinator.data or {}).get(self.mac)
        return {"mac": self.mac, "band": station.get("band")} if station else {"mac": self.mac}
