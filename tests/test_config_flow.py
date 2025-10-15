"""Tests for the ABRP config flow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.abetterrouteplanner.config_flow import (
    ConfigFlow,
    CannotConnect,
    InvalidAuth,
)
from custom_components.abetterrouteplanner.const import (
    CONF_API_KEY,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SESSION_ID,
    CONF_VEHICLE_ID,
    DOMAIN,
)


@pytest.mark.unit
class TestConfigFlowUnit:
    """Unit tests for config flow."""

    async def test_form_display(self, hass):
        """Test that the form is displayed correctly."""
        flow = ConfigFlow()
        flow.hass = hass

        result = await flow.async_step_user(user_input=None)

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "user"
        assert CONF_EMAIL in result["data_schema"].schema
        assert CONF_PASSWORD in result["data_schema"].schema

    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.login"
    )
    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.get_telemetry"
    )
    async def test_successful_login_no_vehicles(
        self, mock_get_telemetry, mock_login, hass, test_email, test_password
    ):
        """Test successful login with no vehicles."""
        # Mock login response without vehicles
        mock_login.return_value = {
            "session_id": "test_session_123",
            "vehicles": [],
        }
        mock_get_telemetry.return_value = {"tlm": {}}

        flow = ConfigFlow()
        flow.hass = hass

        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: test_email,
                CONF_PASSWORD: test_password,
            }
        )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["title"] == f"ABRP - {test_email}"
        assert result["data"][CONF_EMAIL] == test_email
        assert result["data"][CONF_SESSION_ID] == "test_session_123"

    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.login"
    )
    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.get_telemetry"
    )
    async def test_successful_login_with_vehicles(
        self, mock_get_telemetry, mock_login, hass, test_email, test_password
    ):
        """Test successful login with vehicles triggers vehicle selection."""
        # Mock login response with vehicles
        mock_login.return_value = {
            "session_id": "test_session_123",
            "vehicles": [
                {"id": "12345", "name": "Tesla Model 3"},
                {"id": "67890", "name": "Nissan Leaf"},
            ],
        }
        mock_get_telemetry.return_value = {"tlm": {}}

        flow = ConfigFlow()
        flow.hass = hass

        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: test_email,
                CONF_PASSWORD: test_password,
            }
        )

        # Should go to vehicle selection step
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "select_vehicle"

    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.login"
    )
    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.get_telemetry"
    )
    async def test_vehicle_selection(
        self, mock_get_telemetry, mock_login, hass, test_email, test_password
    ):
        """Test vehicle selection step."""
        mock_login.return_value = {
            "session_id": "test_session_123",
            "vehicles": [
                {"id": "12345", "name": "Tesla Model 3"},
                {"id": "67890", "name": "Nissan Leaf"},
            ],
        }
        mock_get_telemetry.return_value = {"tlm": {}}

        flow = ConfigFlow()
        flow.hass = hass

        # First step - login
        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: test_email,
                CONF_PASSWORD: test_password,
            }
        )

        # Second step - vehicle selection
        result = await flow.async_step_select_vehicle(
            user_input={CONF_VEHICLE_ID: "12345"}
        )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["title"] == f"ABRP - {test_email}"
        assert result["data"][CONF_VEHICLE_ID] == "12345"
        assert result["data"][CONF_SESSION_ID] == "test_session_123"

    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.login"
    )
    async def test_invalid_credentials(self, mock_login, hass, test_email):
        """Test login with invalid credentials."""
        from custom_components.abetterrouteplanner.api import InvalidAuth as ApiInvalidAuth

        mock_login.side_effect = ApiInvalidAuth("Invalid credentials")

        flow = ConfigFlow()
        flow.hass = hass

        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: test_email,
                CONF_PASSWORD: "wrongpassword",
            }
        )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"]["base"] == "invalid_auth"

    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.login"
    )
    async def test_connection_error(self, mock_login, hass, test_email, test_password):
        """Test login with connection error."""
        from custom_components.abetterrouteplanner.api import CannotConnect as ApiCannotConnect

        mock_login.side_effect = ApiCannotConnect("Connection failed")

        flow = ConfigFlow()
        flow.hass = hass

        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: test_email,
                CONF_PASSWORD: test_password,
            }
        )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"]["base"] == "cannot_connect"

    @patch(
        "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.login"
    )
    async def test_custom_api_key(
        self, mock_login, hass, test_email, test_password
    ):
        """Test login with custom API key."""
        custom_api_key = "custom_key_12345"

        mock_login.return_value = {
            "session_id": "test_session_123",
            "vehicles": [],
        }

        with patch(
            "custom_components.abetterrouteplanner.config_flow.ABRPApiClient.get_telemetry"
        ) as mock_get_telemetry:
            mock_get_telemetry.return_value = {"tlm": {}}

            flow = ConfigFlow()
            flow.hass = hass

            result = await flow.async_step_user(
                user_input={
                    CONF_EMAIL: test_email,
                    CONF_PASSWORD: test_password,
                    CONF_API_KEY: custom_api_key,
                }
            )

            assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
            assert result["data"][CONF_API_KEY] == custom_api_key


@pytest.mark.integration
class TestConfigFlowIntegration:
    """Integration tests for config flow (requires real credentials)."""

    async def test_real_config_flow(
        self, enable_integration_tests, hass, test_email, test_password, test_api_key
    ):
        """Test config flow with real credentials."""
        if not enable_integration_tests:
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=true")

        flow = ConfigFlow()
        flow.hass = hass

        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: test_email,
                CONF_PASSWORD: test_password,
                CONF_API_KEY: test_api_key,
            }
        )

        # Could be either CREATE_ENTRY (no vehicles) or FORM (vehicle selection)
        assert result["type"] in [
            data_entry_flow.FlowResultType.CREATE_ENTRY,
            data_entry_flow.FlowResultType.FORM,
        ]

        if result["type"] == data_entry_flow.FlowResultType.FORM:
            print(f"\nVehicle selection required")
            print(f"Available vehicles: {len(flow._login_info.get('vehicles', []))}")
        else:
            print(f"\nConfig entry created successfully")
            print(f"Session ID: {result['data'][CONF_SESSION_ID]}")
