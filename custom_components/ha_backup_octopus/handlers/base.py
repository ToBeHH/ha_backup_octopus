import os
import logging
from functools import partial

_LOGGER = logging.getLogger(__name__)


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

        # Create folder in executor to avoid blocking the event loop
        try:
            await self.hass.async_add_executor_job(partial(os.makedirs, self.backup_folder, exist_ok=True))
        except Exception:
            # fallback: try synchronous make (should be rare)
            try:
                os.makedirs(self.backup_folder, exist_ok=True)
            except Exception:
                _LOGGER.exception(
                    "Could not create backup folder: %s", self.backup_folder)

        try:
            await self.fetch_backup(self.backup_folder)
            return True
        except Exception:
            _LOGGER.exception("Error during backup of %s", self.device_name)
            return False
