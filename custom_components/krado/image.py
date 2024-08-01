"""Krado image entity."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.image import ImageEntity, ImageEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import KradoCoordinator
from .entity import KradoEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Krado camera using config entry."""
    coordinator: KradoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            KradoImageEntity(coordinator, IMAGE, plant["id"])
            for plant in coordinator.data
            if plant.get("plantClassification", {}).get("illustrationUrl")
        ]
    )


IMAGE = ImageEntityDescription(key="image", name=None)


class KradoImageEntity(KradoEntity, ImageEntity):
    """Krado image entity."""

    def __init__(
        self,
        coordinator: KradoCoordinator,
        description: ImageEntityDescription,
        plant_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, description, plant_id)
        ImageEntity.__init__(self, coordinator.hass)

    @property
    def image_url(self) -> str:
        """Return URL of image."""
        return self.plant.get("plantClassification", {}).get("illustrationUrl")
