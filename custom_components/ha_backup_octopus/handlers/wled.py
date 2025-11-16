import aiohttp
from .base import DeviceBackupHandler


class WLEDBackupHandler(DeviceBackupHandler):
    def __init__(self, hass, device_name, ip_address) -> None:
        super().__init__(hass, device_name, ip_address)

    async def fetch_backup(self, folder) -> None:
        async with aiohttp.ClientSession() as session:
            cfg_url: str = f"http://{self.device_id}/cfg.json"
            presets_url: str = f"http://{self.device_id}/presets.json"

            async with session.get(cfg_url) as resp:
                cfg_data: bytes = await resp.read()
            async with session.get(presets_url) as resp:
                presets_data: bytes = await resp.read()

        # save both files to disk
        with open(f"{folder}/cfg.json", "wb") as f:
            f.write(cfg_data)
        with open(f"{folder}/presets.json", "wb") as f:
            f.write(presets_data)
