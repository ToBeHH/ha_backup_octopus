import asyncio
import json
import os
import pathlib
import tempfile

from custom_components.ha_backup_octopus.handlers.generic_download import (
    GenericDownloadBackupHandler,
)


class _MockResp:
    def __init__(self, data: bytes, status: int = 200):
        self._data = data
        self.status = status

    async def read(self):
        return self._data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _MockSession:
    def __init__(self, payloads):
        self.payloads = payloads
        self.closed = False

    def get(self, url: str):
        return _MockResp(self.payloads.get(url, b""))

    async def close(self):
        self.closed = True


class _MockConfig:
    def __init__(self, base):
        self.base = base

    def path(self, rel_path: str):
        return os.path.join(self.base, rel_path)


class _MockHass:
    def __init__(self, base):
        self.config = _MockConfig(base)

    async def async_add_executor_job(self, func, *args, **kwargs):
        return func(*args, **kwargs)


async def test_generic_download_backup():
    td = tempfile.TemporaryDirectory()
    base = pathlib.Path(td.name)

    config_path = base / "ha_backup_octopus_backups" / "generic_downloads.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    downloads = [
        {
            "folder": "generic-downloads",
            "url": "http://example.com/frontcam.cfg",
            "filename": "frontcam.cfg",
        },
        {
            "folder": "generic-downloads",
            "url": "http://example.com/system.json",
            "filename": "system.json",
        },
    ]
    config = {"downloads": downloads}
    config_path.write_text(json.dumps(config), encoding="utf-8")

    hass = _MockHass(str(base))

    entries = GenericDownloadBackupHandler.find_entries(hass)
    assert len(entries) == 1

    handlers = GenericDownloadBackupHandler.create_handlers_from_entry(
        hass, entries[0])
    assert len(handlers) == 1
    handler = handlers[0]

    payloads = {
        downloads[0]["url"]: b'{"frontcam":"cfg"}',
        downloads[1]["url"]: b'{"system":"cfg"}',
    }
    session = _MockSession(payloads)

    async def _fake_get_clientsession():
        return session, True

    handler.get_clientsession = _fake_get_clientsession

    result = await handler.run_backup()
    assert result is True

    frontcam = (
        base
        / "ha_backup_octopus_backups"
        / handler.device_name
        / handler.device_id
        / "generic-downloads"
        / "frontcam.cfg"
    )
    system_cfg = (
        base
        / "ha_backup_octopus_backups"
        / handler.device_name
        / handler.device_id
        / "generic-downloads"
        / "system.json"
    )

    assert frontcam.exists()
    assert system_cfg.exists()
    assert frontcam.read_bytes() == payloads[downloads[0]["url"]]
    assert system_cfg.read_bytes() == payloads[downloads[1]["url"]]
    assert session.closed is True


async def test_generic_download_missing_config_disables_handler():
    td = tempfile.TemporaryDirectory()
    hass = _MockHass(td.name)

    entries = GenericDownloadBackupHandler.find_entries(hass)
    assert len(entries) == 1

    handlers = GenericDownloadBackupHandler.create_handlers_from_entry(
        hass, entries[0])
    assert len(handlers) == 1
    handler = handlers[0]

    result = await handler.run_backup()
    assert result is True


if __name__ == "__main__":
    asyncio.run(test_generic_download_backup())
    asyncio.run(test_generic_download_missing_config_disables_handler())
