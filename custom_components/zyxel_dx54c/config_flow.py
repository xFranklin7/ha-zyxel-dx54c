"""Config flow for Zyxel routers."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback

from .api import ZyxelDX54CAPI, ZyxelError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN, MAX_SCAN_INTERVAL, MIN_SCAN_INTERVAL


class ZyxelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up a local Zyxel router."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip().rstrip("/")
            if not host.startswith(("http://", "https://")):
                host = "http://" + host
            api = ZyxelDX54CAPI(host, user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
            try:
                await api.async_get_stations()
            except ZyxelError:
                errors["base"] = "cannot_connect"
            finally:
                await api.async_close()
            if not errors:
                await self.async_set_unique_id(host.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Zyxel ({host})",
                    data={CONF_HOST: host, CONF_USERNAME: user_input[CONF_USERNAME],
                          CONF_PASSWORD: user_input[CONF_PASSWORD]},
                    options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
                )
        schema = vol.Schema({
            vol.Required(CONF_HOST, default="192.168.1.1"): str,
            vol.Required(CONF_USERNAME, default="admin"): str,
            vol.Required(CONF_PASSWORD): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return ZyxelOptionsFlow()


class ZyxelOptionsFlow(config_entries.OptionsFlowWithReload):
    """Configure polling options and reload the entry automatically."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
            )): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL))
        })
        return self.async_show_form(step_id="init", data_schema=schema)
