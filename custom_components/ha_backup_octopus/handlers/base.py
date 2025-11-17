import os
import logging
import json
from functools import partial

_LOGGER = logging.getLogger(__name__)


class DeviceBackupHandler:
    def __init__(self, hass, device_name, device_id, backup_folder=None, entry=None) -> None:
        self.hass = hass
        self.device_name = device_name
        self.device_id = device_id
        self.backup_folder = backup_folder
        # optional: the config entry object associated with this handler
        self.entry = entry

    async def fetch_backup(self, folder) -> None:
        """Return backup data as dictionary."""
        raise NotImplementedError

    @classmethod
    def config_entry_domain(cls) -> str | None:
        """Return the config entry domain this handler understands.

        Return None if the handler does not use config entries.
        """
        return None

    @classmethod
    def find_entries(cls, hass):
        """Return a list of config entries for this handler's domain.

        Default implementation uses `hass.config_entries.async_entries`.
        """
        domain = cls.config_entry_domain()
        if not domain:
            return []
        try:
            return hass.config_entries.async_entries(domain)
        except Exception:
            _LOGGER.exception("Error finding config entries for %s", domain)
            return []

    @classmethod
    def create_handlers_from_entry(cls, hass, entry):
        """Create one or more handler instances from a config entry.

        Return a list (possibly empty) of handler instances. Subclasses
        should override this to extract the needed connection info from
        the entry and construct handler objects.
        """
        return []

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

        # Write the config entry (if any) into entry.json for reproducibility
        if getattr(self, "entry", None) is not None:
            def _write_entry_file():
                try:
                    # Prefer ConfigEntry.as_dict() if available (Home Assistant)
                    if hasattr(self.entry, "as_dict") and callable(getattr(self.entry, "as_dict")):
                        info = self.entry.as_dict()
                    else:
                        # Best-effort fallback: capture common attributes
                        info = {
                            "entry_id": getattr(self.entry, "entry_id", None),
                            "domain": getattr(self.entry, "domain", None),
                            "title": getattr(self.entry, "title", None),
                            "data": getattr(self.entry, "data", None),
                            "options": getattr(self.entry, "options", None),
                            "version": getattr(self.entry, "version", None),
                            "unique_id": getattr(self.entry, "unique_id", None),
                        }

                    with open(os.path.join(self.backup_folder, "entry.json"), "w", encoding="utf-8") as fh:
                        # Use default=str to avoid serialization errors for unknown types
                        json.dump(info, fh, ensure_ascii=False,
                                  indent=2, default=str)
                except Exception:
                    _LOGGER.exception(
                        "Failed to write entry.json for %s", self.device_name)

            await self.hass.async_add_executor_job(_write_entry_file)

        try:
            await self.fetch_backup(self.backup_folder)
            return True
        except Exception:
            _LOGGER.exception("Error during backup of %s", self.device_name)
            return False
