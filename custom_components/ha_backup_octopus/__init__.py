DOMAIN = "ha_backup_octopus"

from homeassistant.core import HomeAssistant


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the device backup integration."""
    hass.data["device_backups"] = {}
    return True
