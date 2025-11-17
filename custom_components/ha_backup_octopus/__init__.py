from .handlers.wled import WLEDBackupHandler
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

    # Discover WLED devices from existing WLED config entries.
    async def _discover_wled_devices() -> None:
        entries = hass.config_entries.async_entries("wled")
        for entry in entries:
            name = entry.title or f"wled-{entry.entry_id}"
            # Common keys used by WLED config entries
            host = entry.data.get("host") or entry.data.get(
                "ip_address") or entry.data.get("host_ip") or entry.data.get("host_name")
            if not host:
                # Try to find a device in the device registry attached to this config entry
                try:
                    from homeassistant.helpers import device_registry as dr

                    registry = dr.async_get(hass)
                    for dev in registry.devices.values():
                        if entry.entry_id in dev.config_entries:
                            name = dev.name or name
                            if dev.configuration_url and isinstance(dev.configuration_url, str):
                                try:
                                    import urllib.parse as _up

                                    parsed = _up.urlparse(
                                        dev.configuration_url)
                                    if parsed.hostname:
                                        host = parsed.hostname
                                except Exception:
                                    pass
                            break
                except Exception:
                    pass

            if not host:
                hass.logger.warning(
                    "WLED config entry %s has no host info; handler not registered",
                    entry.entry_id,
                )
                continue

            handler = WLEDBackupHandler(hass, name, host)
            manager.register_handler(handler)

    hass.async_create_task(_discover_wled_devices())

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
