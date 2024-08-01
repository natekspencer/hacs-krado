"""Krado sensor entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import KradoCoordinator
from .entity import KradoEntity

PLANT_MEASUREMENT_STATUS_LIST = ["Low", "Good", "High"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Krado sensors using config entry."""
    coordinator: KradoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            KradoSensorEntity(coordinator, descriptor, plant["id"])
            for plant in coordinator.data
            if plant["sensor"]["isConnected"]
            for descriptor in DESCRIPTORS
        ]
    )


@dataclass(frozen=True, kw_only=True)
class KradoSensorEntityDescription(SensorEntityDescription):
    """Krado sensor entity description"""

    field: str
    is_reading: bool = True
    range_field: str | None = None


DESCRIPTORS = (
    KradoSensorEntityDescription(
        key="battery",
        field="battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KradoSensorEntityDescription(
        key="humidity",
        field="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KradoSensorEntityDescription(
        key="humidity_status",
        field="humidityStatus",
        is_reading=False,
        range_field="humidityRange",
        translation_key="humidity_status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=PLANT_MEASUREMENT_STATUS_LIST,
    ),
    KradoSensorEntityDescription(
        key="last_analyzed",
        field="lastAnalyzedAt",
        is_reading=False,
        translation_key="last_analyzed",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KradoSensorEntityDescription(
        key="last_reading",
        field="createdAt",
        translation_key="last_reading",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KradoSensorEntityDescription(
        key="light",
        field="light",
        translation_key="light",
        native_unit_of_measurement="μmol/m²/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    KradoSensorEntityDescription(
        key="light_status",
        field="lightStatus",
        is_reading=False,
        range_field="lightRange",
        translation_key="light_status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=PLANT_MEASUREMENT_STATUS_LIST,
    ),
    KradoSensorEntityDescription(
        key="moisture",
        field="moisture",
        translation_key="moisture",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KradoSensorEntityDescription(
        key="moisture_status",
        field="moistureStatus",
        is_reading=False,
        range_field="moistureRange",
        translation_key="moisture_status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=PLANT_MEASUREMENT_STATUS_LIST,
    ),
    KradoSensorEntityDescription(
        key="signal",
        field="signal",
        translation_key="signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KradoSensorEntityDescription(
        key="temperature",
        field="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    KradoSensorEntityDescription(
        key="temperature_status",
        field="temperatureStatus",
        is_reading=False,
        range_field="temperatureRange",
        translation_key="temperature_status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=PLANT_MEASUREMENT_STATUS_LIST,
    ),
)


class KradoSensorEntity(KradoEntity, SensorEntity):
    """Krado sensor entity."""

    entity_description: KradoSensorEntityDescription

    def __init__(
        self,
        coordinator: KradoCoordinator,
        description: KradoSensorEntityDescription,
        plant_id: str,
    ) -> None:
        """Construct a Krado sensor entity."""
        super().__init__(coordinator, description, plant_id)
        if description.range_field:
            low, high = self.plant["sensor"][description.range_field]
            self._attr_extra_state_attributes = {"low": low, "high": high}

    @property
    def native_value(self) -> int | str | None:
        """Return the value reported by the sensor."""
        data = self.plant
        if self.entity_description.is_reading:
            data = data["sensor"]["lastReading"]
        value = data[self.entity_description.field]
        if self.device_class == SensorDeviceClass.TIMESTAMP:
            return datetime.fromisoformat(value)
        if self.device_class == SensorDeviceClass.ENUM and value not in self.options:
            return None
        return value
