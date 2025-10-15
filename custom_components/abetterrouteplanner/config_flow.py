"""Config flow for A Better Route Planner integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ABRPApiClient, CannotConnect as ApiCannotConnect, InvalidAuth as ApiInvalidAuth
from .const import (
    CONF_API_KEY,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SESSION_ID,
    CONF_VEHICLE_ID,
    CONF_VEHICLES,
    DEFAULT_API_KEY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SESSION_ID): str,
        vol.Optional(CONF_VEHICLE_ID): str,
        vol.Optional(CONF_API_KEY, default=DEFAULT_API_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api_key = data.get(CONF_API_KEY, DEFAULT_API_KEY)
    session_id = data[CONF_SESSION_ID]
    vehicle_id = data.get(CONF_VEHICLE_ID)

    client = ABRPApiClient(session, api_key)

    try:
        # Test the session by fetching telemetry
        telemetry_data = await client.get_telemetry(session_id, vehicle_id)

        _LOGGER.debug("Telemetry response: %s", telemetry_data)

        # Extract vehicle info from response if available
        vehicles = []
        if "result" in telemetry_data:
            for vehicle_data in telemetry_data["result"]:
                vehicle_info = {
                    "id": str(vehicle_data.get("vehicle_id", "")),
                    "name": vehicle_data.get("name", f"Vehicle {vehicle_data.get('vehicle_id')}"),
                }
                vehicles.append(vehicle_info)

        return {
            "title": "A Better Route Planner",
            "session_id": session_id,
            "vehicle_id": vehicle_id,
            "vehicles": vehicles,
            "api_key": api_key,
        }

    except ApiCannotConnect as err:
        _LOGGER.error("Cannot connect to ABRP: %s", err)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for A Better Route Planner."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._login_info: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - enter session_id."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Create the config entry
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_SESSION_ID: info["session_id"],
                        CONF_VEHICLE_ID: info.get("vehicle_id"),
                        CONF_API_KEY: info["api_key"],
                    },
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )



class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
