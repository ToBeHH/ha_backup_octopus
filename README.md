# Development
homeassistant:
  name: DevHA

## Set up home assistant
Start HomeAssistant with running
```bash
docker compose up -d
```

Modify the configuration file in the config folder and add detailed logging:
```yaml
logger:
  default: info
  logs:
    custom_components.ha_backup_octopus: debug
```

# Legal

The octopus from the icon is taken from openclipart.org/245075