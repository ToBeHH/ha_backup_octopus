from __future__ import annotations

from typing import Any

from homeassistant import config_entries

from . import DOMAIN


class HaBackupOctopusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Backup Octopus.

    This is intentionally minimal: it only creates an empty config entry so
    the integration is loaded and can discover handlers (WLED config entries).
    """

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is None:
            return self.async_show_form(step_id="user")

        # No configuration required; create an empty entry so async_setup runs.
        return self.async_create_entry(title="HA Backup Octopus", data={})
