from .handlers import AVAILABLE_HANDLERS
from .backup_manager import BackupManager
from homeassistant.core import HomeAssistant
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ha_backup_octopus"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the device backup integration.

    This setup creates a BackupManager, registers a service to trigger
    backups and discovers WLED devices from installed WLED config entries.
    """
    manager = BackupManager(hass)
    hass.data[DOMAIN] = manager

    # sentinel removed: diagnostic file write was temporary and has been cleaned up

    # Register a service to manually trigger backups: ha_backup_octopus.run_backups
    async def _run_backups_service(call):
        await manager.run_backups()

    hass.services.async_register(
        DOMAIN, "run_backups", lambda call: hass.async_create_task(_run_backups_service(call)))

    # Discover handlers by asking each available handler class to find
    # matching config entries and return handler instances. This keeps
    # integration-level code generic and moves provider-specific logic
    # into the handler classes.
    async def _discover_handlers() -> None:
        for handler_cls in AVAILABLE_HANDLERS:
            try:
                entries = handler_cls.find_entries(hass)
            except Exception:
                _LOGGER.exception(
                    "Error while finding entries for %s", handler_cls)
                entries = []

            for entry in entries:
                try:
                    created = handler_cls.create_handlers_from_entry(
                        hass, entry)
                    for h in created:
                        manager.register_handler(h)
                except Exception:
                    _LOGGER.exception(
                        "Failed to create handler(s) from entry %s for %s",
                        getattr(entry, "entry_id", entry),
                        handler_cls,
                    )

    hass.async_create_task(_discover_handlers())

    # Ensure the custom button platform is loaded programmatically so the
    # UI button entity is created without requiring YAML configuration.
    async def _delayed_load():
        try:
            import asyncio

            await asyncio.sleep(1)
            from homeassistant.helpers import discovery as _discovery

            _LOGGER.info("Loading button platform for %s", DOMAIN)
            await _discovery.async_load_platform(hass, "button", DOMAIN, {}, config)
            _LOGGER.info("Requested button platform load for %s", DOMAIN)
        except Exception:
            hass.logger.exception(
                "Failed to load button platform for %s", DOMAIN)

    hass.async_create_task(_delayed_load())

    # Note: we rely on `async_load_platform` to create the `button` entity.
    # Previously a direct fallback added the entity programmatically; that
    # approach has been removed in favor of a single discovery path to
    # keep startup behavior predictable.

    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up from a config entry (UI flow).

    Create the integration runtime (delegates to `async_setup` when the
    integration is not already initialized). This keeps behavior the
    same whether the integration is added via YAML or the UI.
    """
    if hass.data.get(DOMAIN) is None:
        # Reuse async_setup logic to initialize manager, services and
        # discovery tasks. Pass an empty config dict because config
        # entries carry no extra YAML config for this integration.
        await async_setup(hass, {})

    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry and clean up resources.

    This will unload the button platform we created and remove the
    integration data and service registration.
    """
    # Attempt to unload the platform (button)
    try:
        from homeassistant.helpers import discovery as _discovery

        unloaded = await _discovery.async_unload_platform(hass, "button", DOMAIN, entry)
        _LOGGER.debug("Platform unload result: %s", unloaded)
    except Exception:
        # Some HA versions may not support async_unload_platform; try
        # the component unload path instead.
        try:
            from homeassistant.helpers import entity_platform as _entity_platform

            platform = _entity_platform.async_get_platform(
                hass, "button", DOMAIN)
            if platform is not None:
                await platform.async_remove_entities([])
        except Exception:
            _LOGGER.debug("Could not use platform-specific unload; continuing")

    # Remove service if registered
    try:
        hass.services.async_remove(DOMAIN, "run_backups")
    except Exception:
        pass

    # Clean up stored data
    if DOMAIN in hass.data:
        try:
            manager = hass.data.get(DOMAIN)
            if manager is not None:
                try:
                    await manager.shutdown()
                except Exception:
                    _LOGGER.exception(
                        "Error during manager.shutdown() for %s", DOMAIN)

            del hass.data[DOMAIN]
        except Exception:
            _LOGGER.exception("Failed to clear hass.data for %s", DOMAIN)

    return True
