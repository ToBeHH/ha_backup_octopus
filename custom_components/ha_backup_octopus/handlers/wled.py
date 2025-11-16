from .base import DeviceBackupHandler


class WLEDBackupHandler(DeviceBackupHandler):
    async def fetch_backup(self) -> bytes:
        # stub: just return dummy data
        await asyncio.sleep(1)
        return b'{"state":"on"}'
