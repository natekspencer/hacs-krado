"""Diagnostics support for Krado."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics.util import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import KradoCoordinator

TO_REDACT = {
    "id",
    "serialNumber",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: KradoCoordinator = hass.data[DOMAIN][entry.entry_id]
    return async_redact_data(coordinator.data, TO_REDACT)
