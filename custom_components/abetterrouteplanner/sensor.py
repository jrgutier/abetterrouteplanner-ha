"""Support for A Better Route Planner sensors."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfSpeed,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ABRPDataUpdateCoordinator
from .const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_SPEED,
    ATTR_SOC,
    ATTR_POWER,
    ATTR_IS_CHARGING,
    ATTR_VOLTAGE,
    ATTR_CURRENT,
    ATTR_EXT_TEMP,
    ATTR_BATT_TEMP,
    ATTR_SOH,
    ATTR_EST_BATTERY_RANGE,
    ATTR_ELEVATION,
    ATTR_CAR_MODEL,
    ATTR_UTC,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ABRP sensors based on a config entry."""
    coordinator: ABRPDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        ABRPSensor(
            coordinator,
            "State of Charge",
            ATTR_SOC,
            PERCENTAGE,
            SensorDeviceClass.BATTERY,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Speed",
            ATTR_SPEED,
            UnitOfSpeed.KILOMETERS_PER_HOUR,
            SensorDeviceClass.SPEED,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Latitude",
            ATTR_LATITUDE,
            None,
            None,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Longitude",
            ATTR_LONGITUDE,
            None,
            None,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Power",
            ATTR_POWER,
            UnitOfPower.KILO_WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Charging Status",
            ATTR_IS_CHARGING,
            None,
            None,
            None,
        ),
        ABRPSensor(
            coordinator,
            "Voltage",
            ATTR_VOLTAGE,
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Current",
            ATTR_CURRENT,
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "External Temperature",
            ATTR_EXT_TEMP,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Battery Temperature",
            ATTR_BATT_TEMP,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "State of Health",
            ATTR_SOH,
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Estimated Battery Range",
            ATTR_EST_BATTERY_RANGE,
            UnitOfLength.KILOMETERS,
            SensorDeviceClass.DISTANCE,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Elevation",
            ATTR_ELEVATION,
            UnitOfLength.METERS,
            SensorDeviceClass.DISTANCE,
            SensorStateClass.MEASUREMENT,
        ),
        ABRPSensor(
            coordinator,
            "Car Model",
            ATTR_CAR_MODEL,
            None,
            None,
            None,
        ),
        ABRPSensor(
            coordinator,
            "Last Update",
            ATTR_UTC,
            None,
            SensorDeviceClass.TIMESTAMP,
            None,
        ),
    ]

    async_add_entities(sensors)


class ABRPSensor(CoordinatorEntity, SensorEntity):
    """Representation of an ABRP sensor."""

    def __init__(
        self,
        coordinator: ABRPDataUpdateCoordinator,
        name: str,
        data_key: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"ABRP {name}"
        self._attr_unique_id = f"{coordinator.session_id}_{data_key}"
        self._data_key = data_key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        # Handle nested data structure
        tlm_data = self.coordinator.data.get("tlm", {})

        value = tlm_data.get(self._data_key)

        # Convert UTC timestamp to datetime
        if self._data_key == ATTR_UTC and value:
            return datetime.fromtimestamp(value)

        # Convert is_charging to boolean text
        if self._data_key == ATTR_IS_CHARGING and value is not None:
            return "Charging" if value == 1 else "Not Charging"

        return value

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        tlm_data = self.coordinator.data.get("tlm", {})

        # Add relevant contextual data for location sensors
        if self._data_key in [ATTR_LATITUDE, ATTR_LONGITUDE]:
            return {
                "latitude": tlm_data.get(ATTR_LATITUDE),
                "longitude": tlm_data.get(ATTR_LONGITUDE),
                "elevation": tlm_data.get(ATTR_ELEVATION),
                "speed": tlm_data.get(ATTR_SPEED),
            }

        return {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
        )
