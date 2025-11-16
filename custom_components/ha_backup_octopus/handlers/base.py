import os


class DeviceBackupHandler:
    def __init__(self, hass, device_name, device_id, backup_folder=None) -> None:
        self.hass = hass
        self.device_name = device_name
        self.device_id = device_id
        self.backup_folder = backup_folder

    async def fetch_backup(self, folder) -> None:
        """Return backup data as dictionary."""
        raise NotImplementedError

    async def run_backup(self) -> None:
        # Determine backup folder
        if self.backup_folder is None:
            if self.hass:
                self.backup_folder = self.hass.config.path(
                    f"ha_backup_octopus_backups/{self.device_name}/{self.device_id}"
                )
            else:
                self.backup_folder = os.path.join(
                    os.path.join("backups", self.device_name), self.device_id
                )

        os.makedirs(self.backup_folder, exist_ok=True)

        try:
            await self.fetch_backup(self.backup_folder)
            return True
        except Exception as e:
            print(f"Error during backup of {self.device_name}: {e}")
            return False
