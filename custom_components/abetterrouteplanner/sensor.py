"""Support for A Better Route Planner sensors."""

from __future__ import annotations

from datetime import datetime, timezone
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
    UnitOfEnergy,
    DEGREE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from . import ABRPDataUpdateCoordinator
from .const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_SPEED,
    ATTR_SOC,
    ATTR_SOE,
    ATTR_POWER,
    ATTR_IS_CHARGING,
    ATTR_VOLTAGE,
    ATTR_CURRENT,
    ATTR_EXT_TEMP,
    ATTR_VEHICLE_TEMP,
    ATTR_BATT_TEMP,
    ATTR_CABIN_TEMP,
    ATTR_EST_BATTERY_RANGE,
    ATTR_BATTERY_CAPACITY,
    ATTR_CAR_MODEL,
    ATTR_UTC,
    ATTR_IS_PARKED,
    ATTR_IS_DRIVING,
    ATTR_HEADING,
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

    # Use the vehicle name from telemetry data as the sensor name prefix
    # Fall back to config entry title or "ABRP" if vehicle name not available
    vehicle_name = None
    if coordinator.data:
        vehicle_name = coordinator.data.get("name")
    name_prefix = vehicle_name or entry.title or "ABRP"

    sensors = [
        # Battery & Charging (Primary sensors)
        ABRPSensor(
            coordinator,
            name_prefix,
            "State of Charge",
            ATTR_SOC,
            PERCENTAGE,
            SensorDeviceClass.BATTERY,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "State of Energy",
            ATTR_SOE,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY_STORAGE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Battery Capacity",
            ATTR_BATTERY_CAPACITY,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY_STORAGE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Estimated Battery Range",
            ATTR_EST_BATTERY_RANGE,
            UnitOfLength.KILOMETERS,
            SensorDeviceClass.DISTANCE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Charging Status",
            ATTR_IS_CHARGING,
            None,
            None,
            None,
            None,
        ),
        # Electrical
        ABRPSensor(
            coordinator,
            name_prefix,
            "Voltage",
            ATTR_VOLTAGE,
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Current",
            ATTR_CURRENT,
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Power",
            ATTR_POWER,
            UnitOfPower.KILO_WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        # Temperature
        ABRPSensor(
            coordinator,
            name_prefix,
            "Vehicle Temperature",
            ATTR_VEHICLE_TEMP,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Battery Temperature",
            ATTR_BATT_TEMP,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Cabin Temperature",
            ATTR_CABIN_TEMP,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "External Temperature",
            ATTR_EXT_TEMP,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        # Location & Navigation
        ABRPSensor(
            coordinator,
            name_prefix,
            "Latitude",
            ATTR_LATITUDE,
            None,
            None,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Longitude",
            ATTR_LONGITUDE,
            None,
            None,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Heading",
            ATTR_HEADING,
            DEGREE,
            None,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        # Vehicle State (Primary sensors)
        ABRPSensor(
            coordinator,
            name_prefix,
            "Speed",
            ATTR_SPEED,
            UnitOfSpeed.KILOMETERS_PER_HOUR,
            SensorDeviceClass.SPEED,
            SensorStateClass.MEASUREMENT,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Parking Status",
            ATTR_IS_PARKED,
            None,
            None,
            None,
            None,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Driving Status",
            ATTR_IS_DRIVING,
            None,
            None,
            None,
            None,
        ),
        # Vehicle Info (Diagnostic sensors)
        ABRPSensor(
            coordinator,
            name_prefix,
            "Car Model",
            ATTR_CAR_MODEL,
            None,
            None,
            None,
            EntityCategory.DIAGNOSTIC,
        ),
        ABRPSensor(
            coordinator,
            name_prefix,
            "Last Update",
            ATTR_UTC,
            None,
            SensorDeviceClass.TIMESTAMP,
            None,
            EntityCategory.DIAGNOSTIC,
        ),
    ]

    async_add_entities(sensors)


class ABRPSensor(CoordinatorEntity, SensorEntity):
    """Representation of an ABRP sensor."""

    def __init__(
        self,
        coordinator: ABRPDataUpdateCoordinator,
        name_prefix: str,
        name: str,
        data_key: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        entity_category: EntityCategory | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name_suffix = name  # Store the suffix (e.g., "State of Charge")
        self._fallback_prefix = name_prefix  # Initial prefix as fallback
        self._attr_unique_id = f"{coordinator.session_id}_{data_key}"
        self._data_key = data_key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_entity_category = entity_category

        # For temperature sensors, explicitly allow HA to handle unit conversion
        # by not suggesting a specific unit (this respects user's unit system)
        if device_class == SensorDeviceClass.TEMPERATURE:
            self._attr_suggested_unit_of_measurement = None

        # Only set precision for numeric sensors (those with state_class)
        if state_class is not None:
            self._attr_suggested_display_precision = 1
        self._last_known_value = None

        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.session_id)},
            name=name_prefix,
            manufacturer="A Better Route Planner",
            model=self._get_car_model(),
            configuration_url="https://abetterrouteplanner.com",
        )

    def _get_car_model(self) -> str | None:
        """Get the car model from coordinator data."""
        if self.coordinator.data:
            return self.coordinator.data.get("car_model")
        return None

    @property
    def name(self) -> str:
        """Return the name of the sensor, using vehicle name + ABRP prefix."""
        # Try to get vehicle name from coordinator data
        vehicle_name = None
        if self.coordinator.data:
            vehicle_name = self.coordinator.data.get("name")

        # Always include ABRP to avoid naming conflicts with other integrations
        if vehicle_name:
            prefix = f"{vehicle_name} ABRP"
        else:
            prefix = self._fallback_prefix

        return f"{prefix} {self._name_suffix}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        # Handle car_model which is at root level
        if self._data_key == ATTR_CAR_MODEL:
            return self.coordinator.data.get(self._data_key)

        # Handle nested data structure for telemetry data
        tlm_data = self.coordinator.data.get("tlm", {})

        # Handle external temperature from location.weather.temp
        if self._data_key == ATTR_EXT_TEMP:
            location = tlm_data.get("location", {})
            weather = location.get("weather", {})
            value = weather.get("temp")
        # Handle speed - default to 0 if not present (vehicle is parked)
        elif self._data_key == ATTR_SPEED:
            value = tlm_data.get(self._data_key)
            # If speed is None and vehicle is parked, default to 0
            if value is None:
                is_parked = tlm_data.get("is_parked")
                is_driving = tlm_data.get("is_driving")
                if is_parked or not is_driving:
                    value = 0
        else:
            value = tlm_data.get(self._data_key)

        # Convert UTC timestamp to datetime with timezone
        if self._data_key == ATTR_UTC and value:
            return datetime.fromtimestamp(value, tz=timezone.utc)

        # Convert boolean statuses to human-readable text
        if self._data_key == ATTR_IS_CHARGING and value is not None:
            return "Charging" if value else "Not Charging"

        if self._data_key == ATTR_IS_PARKED and value is not None:
            return "Parked" if value else "Not Parked"

        if self._data_key == ATTR_IS_DRIVING and value is not None:
            return "Driving" if value else "Not Driving"

        # Handle missing values with last known value fallback
        if value is None and self._last_known_value is not None:
            # Use last known value for certain sensors that may be intermittently unavailable
            if self._data_key == ATTR_BATT_TEMP:
                return self._last_known_value

        # Store last known value if current value is not None
        if value is not None:
            self._last_known_value = value

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
                "heading": tlm_data.get(ATTR_HEADING),
                "speed": tlm_data.get(ATTR_SPEED),
            }

        return {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and self.coordinator.data is not None
        )
