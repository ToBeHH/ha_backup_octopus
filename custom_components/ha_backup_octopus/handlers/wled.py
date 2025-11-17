import aiohttp
import aiofiles
from .base import DeviceBackupHandler


class WLEDBackupHandler(DeviceBackupHandler):
    """Handler for WLED devices discovered via the WLED config entry.

    This class provides classmethods so the integration can discover
    matching config entries and create handler instances without the
    integration needing to know the entry structure.
    """

    @classmethod
    def config_entry_domain(cls) -> str:
        return "wled"

    @classmethod
    def create_handlers_from_entry(cls, hass, entry):
        """Create handler(s) from a WLED config entry.

        The entry may contain `host`, `ip_address`, `host_ip`, or
        `host_name`. If not found, the device registry is inspected as a
        fallback (same logic as before, encapsulated here).
        """
        name = entry.title or f"wled-{entry.entry_id}"
        host = entry.data.get("host") or entry.data.get(
            "ip_address") or entry.data.get("host_ip") or entry.data.get("host_name")

        if not host:
            hass.logger.warning(
                "WLED config entry %s has no host info; handler not created",
                entry.entry_id,
            )
            return []

        handler = WLEDBackupHandler(hass, name, host, entry=entry)
        return [handler]

    def __init__(self, hass, device_name, ip_address, entry=None) -> None:
        super().__init__(hass, device_name, ip_address, entry=entry)

    async def fetch_backup(self, folder) -> None:
        async with aiohttp.ClientSession() as session:
            cfg_url: str = f"http://{self.device_id}/cfg.json"
            presets_url: str = f"http://{self.device_id}/presets.json"

            async with session.get(cfg_url) as resp:
                cfg_data: bytes = await resp.read()
            async with session.get(presets_url) as resp:
                presets_data: bytes = await resp.read()

        # save both files to disk asynchronously
        async with aiofiles.open(f"{folder}/cfg.json", "wb") as f:
            await f.write(cfg_data)
        async with aiofiles.open(f"{folder}/presets.json", "wb") as f:
            await f.write(presets_data)
