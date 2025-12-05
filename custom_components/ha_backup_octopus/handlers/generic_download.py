import json
import logging
import os
from functools import partial

import aiofiles

from .base import DeviceBackupHandler

_LOGGER = logging.getLogger(__name__)


class GenericDownloadBackupHandler(DeviceBackupHandler):
    """Download arbitrary files from configured URLs.

    Configuration is loaded from a JSON file under the Home Assistant
    config directory at `ha_backup_octopus_backups/generic_downloads.json`.
    """

    CONFIG_RELATIVE_PATH = os.path.join(
        "ha_backup_octopus_backups", "generic_downloads.json")
    DEFAULT_DEVICE_NAME = "Generic Downloads"
    DEFAULT_DEVICE_ID = "generic-downloads-handler"

    @classmethod
    def _config_path(cls, hass) -> str:
        """Return the expected path to the generic download config file."""
        if hass and getattr(hass, "config", None):
            try:
                return hass.config.path(cls.CONFIG_RELATIVE_PATH)
            except Exception:
                _LOGGER.debug(
                    "Falling back to default path for generic download config")
        return os.path.join("config", cls.CONFIG_RELATIVE_PATH)

    @classmethod
    async def _load_config(cls, hass):
        """Load configuration from disk; return None on failure."""
        path = cls._config_path(hass)
        _LOGGER.info("Generic download: reading config from %s", path)

        def _read_file():
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)

        try:
            if hass and getattr(hass, "async_add_executor_job", None):
                data = await hass.async_add_executor_job(_read_file)
            else:
                data = _read_file()
        except FileNotFoundError:
            _LOGGER.warning(
                "Generic download config not found at %s; handler disabled", path
            )
            return None
        except Exception:
            _LOGGER.exception(
                "Failed to read generic download config at %s; handler disabled", path
            )
            return None

        if not isinstance(data, dict):
            _LOGGER.warning(
                "Generic download config must be a JSON object; handler disabled"
            )
            return None

        downloads = data.get("downloads")

        if not downloads:
            _LOGGER.warning(
                "Generic download config missing required 'downloads'; handler disabled"
            )
            return None

        if not isinstance(downloads, list):
            _LOGGER.warning(
                "Generic download config 'downloads' must be a list; handler disabled"
            )
            return None

        validated = []
        for item in downloads:
            if not isinstance(item, dict):
                _LOGGER.debug(
                    "Skipping non-dict download item in generic config")
                continue
            url = item.get("url")
            filename = item.get("filename") or (
                os.path.basename(url.rstrip("/")) if url else None
            )
            target_folder = item.get("folder")
            if not url or not filename or not target_folder:
                _LOGGER.warning(
                    "Skipping invalid generic download entry without url/filename/folder"
                )
                continue
            validated.append(
                {"url": url, "filename": filename, "folder": target_folder})

        if not validated:
            _LOGGER.warning(
                "No valid downloads found in generic download config; handler disabled"
            )
            return None

        _LOGGER.info(
            "Generic download config loaded with %d entries", len(validated))
        return {"downloads": validated}

    @classmethod
    def find_entries(cls, hass):
        """Return a placeholder entry so the handler is always instantiated.

        Config is loaded lazily at backup time to pick up changes between runs.
        """
        return [None]

    @classmethod
    def create_handlers_from_entry(cls, hass, entry):
        """Create a single handler; downloads are loaded at backup time."""
        return [
            cls(
                hass=hass,
                device_name=cls.DEFAULT_DEVICE_NAME,
                device_id=cls.DEFAULT_DEVICE_ID,
                downloads=None,
            )
        ]

    def __init__(self, hass, device_name, device_id, downloads=None, entry=None) -> None:
        super().__init__(hass, device_name, device_id, entry=entry)
        self.downloads = list(downloads) if downloads else None

    async def _ensure_downloads_loaded(self) -> bool:
        """Load downloads from config if not already set."""
        if self.downloads:
            return True

        cfg = await self._load_config(self.hass)
        if not cfg:
            return False

        downloads = cfg.get("downloads")
        if not downloads:
            return False

        self.downloads = list(downloads)
        return True

    async def fetch_backup(self, folder) -> None:
        _LOGGER.info("Generic backup started")
        loaded = await self._ensure_downloads_loaded()
        if not loaded:
            _LOGGER.warning(
                "Generic download configuration could not be loaded; skipping backup"
            )
            return

        session, close_after = await self.get_clientsession()

        try:
            for item in self.downloads:
                url = item.get("url")
                filename = item.get("filename")
                subfolder = item.get("folder")
                if not url or not filename or not subfolder:
                    raise ValueError(
                        "Download item must include url, filename and folder")

                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise ValueError(
                            f"Failed to download {url}, status {resp.status}"
                        )
                    data: bytes = await resp.read()

                target_dir = os.path.join(folder, subfolder)
                # Ensure per-download folder exists to avoid flat structures
                try:
                    if self.hass:
                        await self.hass.async_add_executor_job(
                            partial(os.makedirs, target_dir, exist_ok=True)
                        )
                    else:
                        os.makedirs(target_dir, exist_ok=True)
                except Exception:
                    _LOGGER.exception("Failed to create folder %s", target_dir)
                    raise

                target_path = os.path.join(target_dir, filename)
                _LOGGER.info("Generic download: saving %s -> %s",
                             url, target_path)
                async with aiofiles.open(target_path, "wb") as fh:
                    await fh.write(data)
        finally:
            if close_after:
                try:
                    await session.close()
                except Exception:
                    # Cleanup best effort; do not raise on close failure
                    pass
