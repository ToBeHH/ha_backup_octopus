# Devcontainer for ha_backup_octopus

This devcontainer builds a development image suitable for working on the `ha_backup_octopus` Home Assistant integration.

What it does
- Installs dev tooling (`git`, `curl`, `wget`, `unzip`, `python3-venv`, `python3-pip`)
- Mounts the repository `config/` and `custom_components/` into the container
- Runs `scripts/install` and `scripts/install-hacs` during `postCreateCommand` (make scripts executable first)

Rebuild the container (in VS Code)
1. Open Command Palette → `Dev Containers: Rebuild Container`

Quick verification after rebuild
```bash
# In the container terminal (VS Code -> Terminal)
ls -la /config/custom_components
source .venv/bin/activate
python -m homeassistant --config ./config
```

Notes
- If HACS installer fails (HA not running in the container during `postCreateCommand`), the devcontainer provides a fallback that clones the HACS integration into `config/custom_components/hacs`.
- You still need to restart Home Assistant after the container build for HACS to be recognized.
