"""Support for Krado."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import KradoCoordinator
from .pykrado import Krado

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.IMAGE,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Krado from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    client = Krado(entry.data[CONF_TOKEN])
    coordinator = KradoCoordinator(hass, client)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.exception(ex)

    if not coordinator.data:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
