class DeviceBackupHandler:
    def __init__(self, hass, device_name):
        self.hass = hass
        self.device_name = device_name

    async def fetch_backup(self) -> bytes:
        """Return backup data for the device."""
        raise NotImplementedError
