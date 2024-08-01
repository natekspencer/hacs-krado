"""Krado coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .pykrado import Krado

_LOGGER = logging.getLogger(__name__)


class KradoCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Krado data update coordinator."""

    def __init__(self, hass: HomeAssistant, client: Krado) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
            always_update=False,
        )
        self.client = client

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            async with async_timeout.timeout(10):
                data = await self.client.query_plants()
        except Exception as ex:
            raise UpdateFailed("Couldn't read from Krado") from ex
        if data is None:
            raise ConfigEntryAuthFailed
        return data
