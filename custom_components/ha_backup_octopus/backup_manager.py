import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class BackupManager:
    def __init__(self, hass) -> None:
        self.hass = hass
        self.device_handlers = []

    def register_handler(self, handler) -> None:
        self.device_handlers.append(handler)

    async def run_backups(self) -> None:
        """Run backups for all registered handlers.

        This calls each handler's `run_backup()` helper which sets up the
        backup folder and then invokes the implementation-specific
        `fetch_backup(folder)` method.
        """
        for handler in self.device_handlers:
            try:
                ok = await handler.run_backup()
                if ok:
                    _LOGGER.info("Backup successful for %s", getattr(
                        handler, "device_name", "<unknown>"))
                else:
                    _LOGGER.warning("Backup failed for %s", getattr(
                        handler, "device_name", "<unknown>"))
            except Exception as exc:  # pragma: no cover - defensive
                _LOGGER.exception("Exception during backup for %s: %s", getattr(
                    handler, "device_name", "<unknown>"), exc)
