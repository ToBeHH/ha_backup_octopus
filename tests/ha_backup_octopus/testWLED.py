import asyncio
import tempfile
import pathlib

from custom_components.ha_backup_octopus.handlers.wled import WLEDBackupHandler


class _MockResp:
    def __init__(self, data: bytes):
        self._data = data

    async def read(self):
        return self._data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _MockSession:
    def get(self, url: str):
        # return predictable mock payloads for cfg and presets
        if url.endswith("/cfg.json"):
            return _MockResp(b'{"mock":"cfg"}')
        if url.endswith("/presets.json"):
            return _MockResp(b'{"mock":"presets"}')
        return _MockResp(b"{}")

    async def close(self):
        return None


async def test_wled_backup():
    # Use a temporary directory for backups so the test is hermetic
    td = tempfile.TemporaryDirectory()
    backups_root = pathlib.Path(td.name)

    handler = WLEDBackupHandler(None, "WLED Living Room", "192.168.173.133")

    # Patch the handler's get_clientsession to return our mock session
    async def _fake_get_clientsession():
        return _MockSession(), True

    handler.get_clientsession = _fake_get_clientsession

    # Provide a deterministic backup folder
    handler.backup_folder = str(
        backups_root / "ha_backup_octopus_backups" / handler.device_name / handler.device_id)

    result: bool = await handler.run_backup()
    print(f"WLED Backup Result: {result}")

    assert result is True
    # Verify files were written
    cfg = backups_root / "ha_backup_octopus_backups" / \
        handler.device_name / handler.device_id / "cfg.json"
    presets = backups_root / "ha_backup_octopus_backups" / \
        handler.device_name / handler.device_id / "presets.json"
    assert cfg.exists(), f"Expected cfg.json at {cfg}"
    assert presets.exists(), f"Expected presets.json at {presets}"


if __name__ == "__main__":
    asyncio.run(test_wled_backup())
