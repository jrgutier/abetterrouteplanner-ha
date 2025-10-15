"""API client for A Better Route Planner."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://api.iternio.com/1"
WEB_BASE_URL = "https://abetterrouteplanner.com"


class ABRPApiClient:
    """ABRP API Client."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        """Initialize the API client."""
        self.session = session
        self.api_key = api_key

    async def login(self, email: str, password: str, session_id: str = "") -> dict[str, Any]:
        """
        Authenticate with ABRP using email and password.

        This attempts to login to ABRP and extract session information.
        Returns session_id and list of vehicles.

        Note: ABRP uses reCAPTCHA which we cannot automatically solve.
        This method works without reCAPTCHA if you provide an existing session_id.
        """
        auth_url = f"{API_BASE_URL}/session/user_login"

        headers = {
            "accept": "application/json, text/plain, */*",
            "authorization": f"APIKEY {self.api_key}",
            "content-type": "application/json",
            "origin": WEB_BASE_URL,
            "referer": f"{WEB_BASE_URL}/",
        }

        # Use provided session_id or empty string (ABRP creates new session)
        payload = {
            "session_id": session_id,
            "login": email,
            "password": password,
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.post(
                    auth_url, headers=headers, json=payload
                ) as response:
                    if response.status == 401:
                        raise InvalidAuth("Invalid email or password")

                    if response.status == 403:
                        raise InvalidAuth("reCAPTCHA required - please login via browser first")

                    response.raise_for_status()
                    data = await response.json()

                    _LOGGER.debug("Login response: %s", data)

                    # Extract session_id and vehicles from response
                    return await self._extract_session_info(data)

        except aiohttp.ClientError as err:
            _LOGGER.error("Error during login: %s", err)
            raise CannotConnect(f"Unable to connect to ABRP: {err}") from err

    async def _extract_session_info(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract session ID and vehicles from login response."""
        # Common response patterns from various APIs
        session_id = (
            data.get("session_id")
            or data.get("sessionId")
            or data.get("session", {}).get("id")
            or data.get("token")
            or data.get("access_token")
        )

        if not session_id:
            _LOGGER.error("Could not find session_id in response: %s", data)
            raise InvalidAuth("Unable to extract session from login response")

        # Try to get vehicles list
        vehicles = []

        # Check various possible locations for vehicle data
        vehicle_data = (
            data.get("vehicles")
            or data.get("cars")
            or data.get("user", {}).get("vehicles")
            or []
        )

        for vehicle in vehicle_data:
            vehicle_id = vehicle.get("id") or vehicle.get("vehicle_id")
            vehicle_name = vehicle.get("name") or vehicle.get("model") or f"Vehicle {vehicle_id}"

            if vehicle_id:
                vehicles.append({
                    "id": vehicle_id,
                    "name": vehicle_name,
                })

        _LOGGER.info("Found %d vehicles", len(vehicles))

        return {
            "session_id": session_id,
            "vehicles": vehicles,
        }

    async def get_telemetry(
        self, session_id: str, vehicle_id: str | None = None
    ) -> dict[str, Any]:
        """Get telemetry data from ABRP."""
        url = f"{API_BASE_URL}/session/get_tlm"

        headers = {
            "accept": "*/*",
            "authorization": f"APIKEY {self.api_key}",
            "content-type": "application/json",
            "origin": WEB_BASE_URL,
            "referer": f"{WEB_BASE_URL}/",
        }

        payload = {"session_id": session_id}

        if vehicle_id:
            payload["wakeup_vehicle_id"] = int(vehicle_id)

        try:
            async with async_timeout.timeout(10):
                async with self.session.post(
                    url, headers=headers, json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug("Telemetry data: %s", data)
                    return data
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching telemetry: %s", err)
            raise CannotConnect(f"Error fetching telemetry: {err}") from err


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
