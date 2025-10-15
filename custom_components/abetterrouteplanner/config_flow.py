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
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_API_KEY, default=DEFAULT_API_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect and perform login."""
    session = async_get_clientsession(hass)
    api_key = data.get(CONF_API_KEY, DEFAULT_API_KEY)

    client = ABRPApiClient(session, api_key)

    try:
        # Attempt login and get session info
        login_result = await client.login(data[CONF_EMAIL], data[CONF_PASSWORD])

        session_id = login_result["session_id"]
        vehicles = login_result.get("vehicles", [])

        _LOGGER.info("Successfully logged in. Found %d vehicles", len(vehicles))

        # Test the session by fetching telemetry
        vehicle_id = vehicles[0]["id"] if vehicles else None
        await client.get_telemetry(session_id, vehicle_id)

        return {
            "title": f"ABRP - {data[CONF_EMAIL]}",
            "session_id": session_id,
            "vehicles": vehicles,
            "api_key": api_key,
        }

    except ApiInvalidAuth as err:
        _LOGGER.error("Invalid credentials: %s", err)
        raise InvalidAuth from err
    except ApiCannotConnect as err:
        _LOGGER.error("Cannot connect to ABRP: %s", err)
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
        """Handle the initial step - login with email/password."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Store login info for next step
                self._login_info = {
                    CONF_EMAIL: user_input[CONF_EMAIL],
                    CONF_API_KEY: info["api_key"],
                    CONF_SESSION_ID: info["session_id"],
                    CONF_VEHICLES: info["vehicles"],
                }

                # If vehicles found, let user select one
                if info["vehicles"]:
                    return await self.async_step_select_vehicle()

                # No vehicles, create entry with just session
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_API_KEY: info["api_key"],
                        CONF_SESSION_ID: info["session_id"],
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

    async def async_step_select_vehicle(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle vehicle selection step."""
        vehicles = self._login_info[CONF_VEHICLES]

        if user_input is not None:
            selected_vehicle = user_input[CONF_VEHICLE_ID]

            return self.async_create_entry(
                title=f"ABRP - {self._login_info[CONF_EMAIL]}",
                data={
                    CONF_EMAIL: self._login_info[CONF_EMAIL],
                    CONF_API_KEY: self._login_info[CONF_API_KEY],
                    CONF_SESSION_ID: self._login_info[CONF_SESSION_ID],
                    CONF_VEHICLE_ID: selected_vehicle,
                },
            )

        # Build vehicle selection schema
        vehicle_options = {
            str(vehicle["id"]): vehicle["name"] for vehicle in vehicles
        }

        data_schema = vol.Schema(
            {
                vol.Required(CONF_VEHICLE_ID): vol.In(vehicle_options),
            }
        )

        return self.async_show_form(
            step_id="select_vehicle",
            data_schema=data_schema,
            description_placeholders={
                "num_vehicles": str(len(vehicles)),
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
