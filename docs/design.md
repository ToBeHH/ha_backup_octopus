# Home Assistant Device Backup Integration

## Overview
This integration provides asynchronous backup collection from external devices (e.g., WLED controllers, routers, or other network-connected systems) and bundles the latest collected backups into Home Assistant's main snapshots. The goal is to centralize configuration resilience across the home automation ecosystem.

The initial version is implemented as a Home Assistant integration distributed via HACS. Future versions may optionally include an Add-on for advanced backup agents or system-level tooling.

## Objectives
- Collect backup data from supported devices on a scheduled basis.
- Store the latest successful backup for each device locally within the integration.
- Inject cached backups into Home Assistant snapshots without delaying the snapshot process.
- Allow extensibility through Python-based backup handler classes.
- Provide a clean path to introduce an optional Add-on for advanced device types.

## Architecture
### Integration Structure
The project structure follows a standard custom component layout:
```
custom_components/
  ha_device_backups/
    __init__.py
    manifest.json
    backup_manager.py
    handlers/
      base.py
      wled.py
      fritzbox.py
      ... additional handlers ...
    storage/
      ... locally cached backup files ...
```

### Backup Manager
The backup manager orchestrates:
- Scheduling of asynchronous device backup tasks
- Storage and retrieval of cached backup files
- Injection of cached artifacts into Home Assistant snapshots

The manager exposes an internal API for device handlers and interacts with Home Assistant's backup lifecycle.

### Device Backup Handlers
Device support is implemented through Python classes.
Each handler inherits from a common base interface that defines:
```
class DeviceBackupHandler:
    def __init__(self, hass, config):
        self.hass = hass
        self.config = config

    async def fetch_backup(self) -> bytes:
        raise NotImplementedError

    async def test_connection(self) -> bool:
        raise NotImplementedError
```

Handlers return backup data as raw bytes or serialized content. The integration stores these artifacts as timestamped files.

### Scheduler
The integration uses Home Assistant's asynchronous scheduling utilities to run periodic backups. Users may configure:
- Backup frequency
- Per-device schedules
- Whether devices should retry failed backups

### Snapshot Injection
During a Home Assistant backup event:
- The integration collects the most recent cached backup files
- These cached files are injected directly into the snapshot archive
- No device backup operations run during snapshot creation, keeping the process fast and reliable

### Storage
Backups are stored within a dedicated directory under the integration path or Home Assistant's `.storage` area. Each device has its own set of timestamped backup artifacts.

Example:
```
storage/device_id/
  backup_2025-01-15_10-30.json
  backup_2025-01-16_10-30.json
```

## Distribution Path
### Initial Release: HACS Integration
The first version is packaged as a HACS-compatible integration to:
- Enable quick community installation
- Simplify updates
- Encourage early contributions

### Future Option: Add-on
A Home Assistant Add-on may be introduced later for advanced cases such as:
- Running external binaries
- Performing SSH or rsync-based backups
- Handling large or sensitive data outside the HA config directory

The integration would detect and interface with the add-on when available.

## Extensibility
The design enables adding new device handlers by creating new classes under `handlers/` and registering them via the integration's configuration flow. Handlers remain lightweight and network-oriented, allowing the community to contribute without modifying the core architecture.

## Next Steps
- Define configuration flow for adding devices
- Implement the backup manager
- Implement sample handlers (WLED, router device)
- Connect the manager to Home Assistant's snapshot event
- Prepare HACS packaging files

