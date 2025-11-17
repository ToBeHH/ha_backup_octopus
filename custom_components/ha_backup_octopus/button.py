from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN


async def async_setup_platform(hass: HomeAssistant, config, async_add_entities: AddEntitiesCallback, discovery_info=None):
    """Set up the Backup Now button (YAML config).

    This adds a single button entity that triggers the integration's
    BackupManager.run_backups when pressed.
    """
    manager = hass.data.get(DOMAIN)
    if manager is None:
        return

    async_add_entities([BackupNowButton(manager)])


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback):
    """Set up the Backup Now button for config entries (future-proof)."""
    manager = hass.data.get(DOMAIN)
    if manager is None:
        return

    async_add_entities([BackupNowButton(manager)])


class BackupNowButton(ButtonEntity):
    """Button to trigger backups immediately."""

    def __init__(self, manager) -> None:
        self._manager = manager
        self._attr_name = "HA Backup Octopus: Run Backups"
        self._attr_unique_id = "ha_backup_octopus_backup_now"
        # UI friendly icon
        self._attr_icon = "mdi:backup-restore"
        # category and device class are not strictly needed for Button, but entity category helps UI
        self._attr_entity_category = None

    @property
    def should_poll(self) -> bool:
        return False

    async def async_press(self) -> None:
        """Handle the button press by running backups."""
        # run_backups is an async method
        await self._manager.run_backups()
