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
                    _LOGGER.info(
                        "Backup successful for %s",
                        getattr(handler, "device_name", "<unknown>"),
                    )
                else:
                    _LOGGER.warning(
                        "Backup failed for %s",
                        getattr(handler, "device_name", "<unknown>"),
                    )
            except Exception as exc:  # pragma: no cover - defensive
                _LOGGER.exception(
                    "Exception during backup for %s: %s",
                    getattr(handler, "device_name", "<unknown>"),
                    exc,
                )

    async def shutdown(self) -> None:
        """Shutdown the manager and its handlers.

        If handlers implement an async `shutdown()` method it will be
        awaited; if they implement a synchronous `shutdown()` it will
        be called in the executor. Finally the handler list is cleared.
        """
        for handler in list(self.device_handlers):
            try:
                # prefer async shutdown
                shutdown = getattr(handler, "shutdown", None)
                if shutdown is None:
                    continue

                if asyncio.iscoroutinefunction(shutdown):
                    await shutdown()
                else:
                    # run sync shutdown in executor
                    await self.hass.async_add_executor_job(shutdown)
            except Exception:
                _LOGGER.exception(
                    "Error shutting down handler %s",
                    getattr(handler, "device_name", handler),
                )

        # remove handlers list
        self.device_handlers.clear()
