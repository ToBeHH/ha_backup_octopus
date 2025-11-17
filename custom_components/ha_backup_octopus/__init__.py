from .handlers import AVAILABLE_HANDLERS
from .backup_manager import BackupManager
from homeassistant.core import HomeAssistant
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ha_backup_octopus"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the device backup integration.

    This setup creates a BackupManager, registers a service to trigger
    backups and discovers WLED devices from installed WLED config entries.
    """
    manager = BackupManager(hass)
    hass.data[DOMAIN] = manager

    # sentinel removed: diagnostic file write was temporary and has been cleaned up

    # Register a service to manually trigger backups: ha_backup_octopus.run_backups
    async def _run_backups_service(call):
        await manager.run_backups()

    hass.services.async_register(
        DOMAIN, "run_backups", lambda call: hass.async_create_task(_run_backups_service(call)))

    # Discover handlers by asking each available handler class to find
    # matching config entries and return handler instances. This keeps
    # integration-level code generic and moves provider-specific logic
    # into the handler classes.
    async def _discover_handlers() -> None:
        for handler_cls in AVAILABLE_HANDLERS:
            try:
                entries = handler_cls.find_entries(hass)
            except Exception:
                _LOGGER.exception(
                    "Error while finding entries for %s", handler_cls)
                entries = []

            for entry in entries:
                try:
                    created = handler_cls.create_handlers_from_entry(
                        hass, entry)
                    for h in created:
                        manager.register_handler(h)
                except Exception:
                    _LOGGER.exception(
                        "Failed to create handler(s) from entry %s for %s",
                        getattr(entry, "entry_id", entry),
                        handler_cls,
                    )

    hass.async_create_task(_discover_handlers())

    # Ensure the custom button platform is loaded programmatically so the
    # UI button entity is created without requiring YAML configuration.
    async def _delayed_load():
        try:
            import asyncio

            await asyncio.sleep(1)
            from homeassistant.helpers import discovery as _discovery

            _LOGGER.info("Loading button platform for %s", DOMAIN)
            await _discovery.async_load_platform(hass, "button", DOMAIN, {}, config)
            _LOGGER.info("Requested button platform load for %s", DOMAIN)
        except Exception:
            hass.logger.exception(
                "Failed to load button platform for %s", DOMAIN)

    hass.async_create_task(_delayed_load())

    return True
