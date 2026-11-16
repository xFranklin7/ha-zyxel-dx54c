"""Coordinator for router station data."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ZyxelDX54CAPI, ZyxelError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ZyxelDataUpdateCoordinator(DataUpdateCoordinator):
    """Poll the router and retain a registry of seen clients."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.api = ZyxelDX54CAPI(
            entry.data[CONF_HOST], entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
        )
        self.known_stations: dict[str, dict] = {}
        interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=interval)
        )

    async def _async_update_data(self):
        try:
            stations = await self.api.async_get_stations()
        except ZyxelError as err:
            raise UpdateFailed(str(err)) from err
        current = {station["mac"]: station for station in stations}
        self.known_stations.update(current)
        return current

    async def async_shutdown(self) -> None:
        """Close the HTTP session."""
        await self.api.async_close()
