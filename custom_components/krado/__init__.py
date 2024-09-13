"""Support for Krado."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN
from .coordinator import KradoCoordinator
from .pykrado import Krado

type KradoConfigEntry = ConfigEntry[KradoCoordinator]

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.IMAGE,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: KradoConfigEntry) -> bool:
    """Set up Krado from a config entry."""
    client = Krado(entry.data[CONF_TOKEN])
    coordinator = KradoCoordinator(hass, client)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.exception(ex)

    if not coordinator.data:
        raise ConfigEntryNotReady

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: KradoConfigEntry) -> bool:
    """Unload a config entry."""
    await entry.runtime_data.client.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: KradoConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return not any(
        identifier
        for identifier in device_entry.identifiers
        if identifier[0] == DOMAIN
        for plant in entry.runtime_data.data
        if plant["id"] == identifier[1]
    )
