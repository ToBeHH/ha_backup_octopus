import asyncio


class BackupManager:
    def __init__(self, hass) -> None:
        self.hass = hass
        self.device_handlers = []

    def register_handler(self, handler) -> None:
        self.device_handlers.append(handler)

    async def run_backups(self) -> None:
        for handler in self.device_handlers:
            data = await handler.fetch_backup()
            print(f"Backup for {handler.device_name}: {len(data)} bytes")
