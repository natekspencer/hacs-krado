"""Krado entity."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KradoCoordinator

_LOGGER = logging.getLogger(__name__)


class KradoEntity(CoordinatorEntity[KradoCoordinator]):
    """Base class for Krado entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KradoCoordinator,
        description: EntityDescription,
        plant_id: str,
    ) -> None:
        """Construct a Krado entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self.plant_id = plant_id

        sensor = self.plant["sensor"]

        self._attr_unique_id = f"{plant_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, plant_id)},
            name=self.plant["name"],
            manufacturer="Krado",
            model="leaflet" if sensor["isConnected"] else self.plant["kind"],
            serial_number=sensor["serialNumber"],
            sw_version=sensor["firmwareVersion"],
        )

    @property
    def plant(self) -> dict[str, Any]:
        """Get plant data."""
        return next(
            plant for plant in self.coordinator.data if plant["id"] == self.plant_id
        )

    @property
    def available(self) -> bool:
        """Test if entity is available."""
        return super().available and next(
            (plant for plant in self.coordinator.data if plant["id"] == self.plant_id),
            None,
        )
