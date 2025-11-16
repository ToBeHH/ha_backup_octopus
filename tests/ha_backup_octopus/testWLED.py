import asyncio
from custom_components.ha_backup_octopus.handlers.wled import WLEDBackupHandler


async def test_wled_backup():
    handler = WLEDBackupHandler(None, "WLED Living Room", "192.168.173.133")
    result: bool = await handler.run_backup()
    print(f"WLED Backup Result: {result}")


asyncio.run(test_wled_backup())
