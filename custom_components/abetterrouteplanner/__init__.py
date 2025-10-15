"""The A Better Route Planner integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import ABRPApiClient, CannotConnect
from .const import (
    CONF_API_KEY,
    CONF_SESSION_ID,
    CONF_VEHICLE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up A Better Route Planner from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    session_id = entry.data[CONF_SESSION_ID]
    vehicle_id = entry.data.get(CONF_VEHICLE_ID)

    coordinator = ABRPDataUpdateCoordinator(
        hass,
        api_key=api_key,
        session_id=session_id,
        vehicle_id=vehicle_id,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class ABRPDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching ABRP data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        session_id: str,
        vehicle_id: str | None = None,
    ) -> None:
        """Initialize."""
        self.api_key = api_key
        self.session_id = session_id
        self.vehicle_id = vehicle_id
        self.client = ABRPApiClient(async_get_clientsession(hass), api_key)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via ABRP API."""
        try:
            data = await self.client.get_telemetry(self.session_id, self.vehicle_id)
            _LOGGER.debug("Received data from ABRP: %s", data)
            return data
        except CannotConnect as err:
            raise UpdateFailed(f"Error communicating with ABRP API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
