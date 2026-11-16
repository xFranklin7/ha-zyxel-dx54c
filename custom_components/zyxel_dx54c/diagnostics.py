"""Privacy-conscious diagnostics."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return diagnostics without credentials, session tokens, or client MACs."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    stations = coordinator.data or {}
    bands: dict[str, int] = {}
    for station in stations.values():
        band = station.get("band", "unknown")
        bands[band] = bands.get(band, 0) + 1
    return {"router": entry.data.get("host"), "integration": DOMAIN,
            "connected_clients": len(stations), "clients_by_band": bands,
            "update_interval_seconds": entry.options.get("scan_interval", 60),
            "last_update_success": coordinator.last_update_success}
