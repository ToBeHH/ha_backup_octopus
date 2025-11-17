from .handlers.wled import WLEDBackupHandler
from .backup_manager import BackupManager
from homeassistant.core import HomeAssistant
DOMAIN = "ha_backup_octopus"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the device backup integration.

    This minimal setup creates a BackupManager, registers a service to
    trigger backups and optionally registers WLED handlers defined in
    `configuration.yaml` under the `ha_backup_octopus:` key.
    """
    manager = BackupManager(hass)
    hass.data[DOMAIN] = manager

    # Register a service to manually trigger backups: ha_backup_octopus.run_backups
    async def _run_backups_service(call):
        await manager.run_backups()

    hass.services.async_register(
        DOMAIN, "run_backups", lambda call: hass.async_create_task(_run_backups_service(call)))

    # Load device definitions from configuration.yaml (optional)
    conf = config.get(DOMAIN, {}) or {}
    devices = conf.get("devices", [])
    for dev in devices:
        platform = dev.get("platform")
        name = dev.get("name")
        if platform == "wled":
            ip = dev.get("ip")
            if name and ip:
                handler = WLEDBackupHandler(hass, name, ip)
                manager.register_handler(handler)

    return True
