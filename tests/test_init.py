"""Tests for the ABRP integration initialization."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.abetterrouteplanner import (
    async_setup_entry,
    async_unload_entry,
    ABRPDataUpdateCoordinator,
)
from custom_components.abetterrouteplanner.const import (
    CONF_API_KEY,
    CONF_SESSION_ID,
    CONF_VEHICLE_ID,
    DOMAIN,
)


@pytest.mark.unit
class TestInitUnit:
    """Unit tests for integration initialization."""

    @patch("custom_components.abetterrouteplanner.ABRPDataUpdateCoordinator")
    async def test_setup_entry(self, mock_coordinator_class, hass, mock_config_entry):
        """Test successful setup of a config entry."""
        # Mock coordinator instance
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator

        # Mock platform forward
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        result = await async_setup_entry(hass, mock_config_entry)

        assert result is True
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]
        mock_coordinator.async_config_entry_first_refresh.assert_called_once()

    @patch("custom_components.abetterrouteplanner.ABRPDataUpdateCoordinator")
    async def test_unload_entry(self, mock_coordinator_class, hass, mock_config_entry):
        """Test unloading a config entry."""
        # Setup entry first
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator

        hass.config_entries.async_forward_entry_setups = AsyncMock()
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

        await async_setup_entry(hass, mock_config_entry)

        # Now unload
        result = await async_unload_entry(hass, mock_config_entry)

        assert result is True
        assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})


@pytest.mark.unit
class TestDataUpdateCoordinator:
    """Tests for the data update coordinator."""

    @patch("custom_components.abetterrouteplanner.ABRPApiClient")
    async def test_coordinator_update_success(
        self, mock_api_client_class, hass, mock_telemetry_response
    ):
        """Test successful data update."""
        # Mock API client
        mock_client = MagicMock()
        mock_client.get_telemetry = AsyncMock(return_value=mock_telemetry_response)
        mock_api_client_class.return_value = mock_client

        coordinator = ABRPDataUpdateCoordinator(
            hass,
            api_key="test_key",
            session_id="test_session",
            vehicle_id="12345",
        )

        # Trigger update
        await coordinator.async_refresh()

        assert coordinator.data == mock_telemetry_response
        assert coordinator.last_update_success is True

    @patch("custom_components.abetterrouteplanner.ABRPApiClient")
    async def test_coordinator_update_failure(self, mock_api_client_class, hass):
        """Test data update failure."""
        from custom_components.abetterrouteplanner.api import CannotConnect

        # Mock API client to raise error
        mock_client = MagicMock()
        mock_client.get_telemetry = AsyncMock(
            side_effect=CannotConnect("Connection failed")
        )
        mock_api_client_class.return_value = mock_client

        coordinator = ABRPDataUpdateCoordinator(
            hass,
            api_key="test_key",
            session_id="test_session",
        )

        # Trigger update
        await coordinator.async_refresh()

        assert coordinator.last_update_success is False

    @patch("custom_components.abetterrouteplanner.ABRPApiClient")
    async def test_coordinator_with_vehicle_id(
        self, mock_api_client_class, hass, mock_telemetry_response
    ):
        """Test coordinator passes vehicle ID correctly."""
        mock_client = MagicMock()
        mock_client.get_telemetry = AsyncMock(return_value=mock_telemetry_response)
        mock_api_client_class.return_value = mock_client

        coordinator = ABRPDataUpdateCoordinator(
            hass,
            api_key="test_key",
            session_id="test_session",
            vehicle_id="67890",
        )

        await coordinator.async_refresh()

        # Verify vehicle_id was passed to get_telemetry
        mock_client.get_telemetry.assert_called_with("test_session", "67890")

    @patch("custom_components.abetterrouteplanner.ABRPApiClient")
    async def test_coordinator_without_vehicle_id(
        self, mock_api_client_class, hass, mock_telemetry_response
    ):
        """Test coordinator works without vehicle ID."""
        mock_client = MagicMock()
        mock_client.get_telemetry = AsyncMock(return_value=mock_telemetry_response)
        mock_api_client_class.return_value = mock_client

        coordinator = ABRPDataUpdateCoordinator(
            hass, api_key="test_key", session_id="test_session"
        )

        await coordinator.async_refresh()

        # Verify vehicle_id None was passed
        mock_client.get_telemetry.assert_called_with("test_session", None)


@pytest.mark.integration
class TestInitIntegration:
    """Integration tests for initialization (requires real credentials)."""

    async def test_real_coordinator_update(
        self,
        enable_integration_tests,
        hass,
        test_api_key,
        test_email,
        test_password,
        test_vehicle_id,
    ):
        """Test coordinator with real API calls."""
        if not enable_integration_tests:
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=true")

        # First need to login to get session
        import aiohttp
        from custom_components.abetterrouteplanner.api import ABRPApiClient

        async with aiohttp.ClientSession() as session:
            client = ABRPApiClient(session, test_api_key)
            login_result = await client.login(test_email, test_password)
            session_id = login_result["session_id"]

            # Use provided vehicle ID or first from login
            vehicle_id = test_vehicle_id
            if not vehicle_id and login_result["vehicles"]:
                vehicle_id = login_result["vehicles"][0]["id"]

            # Create coordinator
            coordinator = ABRPDataUpdateCoordinator(
                hass,
                api_key=test_api_key,
                session_id=session_id,
                vehicle_id=vehicle_id,
            )

            # Trigger update
            await coordinator.async_config_entry_first_refresh()

            assert coordinator.last_update_success is True
            assert coordinator.data is not None

            print(f"\nCoordinator update successful!")
            if "tlm" in coordinator.data:
                tlm = coordinator.data["tlm"]
                print(f"  SOC: {tlm.get('soc')}%")
                print(f"  Speed: {tlm.get('speed')} km/h")
                print(f"  Location: {tlm.get('latitude')}, {tlm.get('longitude')}")
