"""Tests for the ABRP API client."""
import aiohttp
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.abetterrouteplanner.api import (
    ABRPApiClient,
    CannotConnect,
    InvalidAuth,
)


@pytest.mark.unit
class TestABRPApiClientUnit:
    """Unit tests for ABRP API client (mocked)."""

    async def test_login_success(self, mock_aiohttp_session, mock_login_response):
        """Test successful login."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_login_response)
        mock_response.raise_for_status = MagicMock()

        mock_aiohttp_session.post = AsyncMock(
            return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
        )

        client = ABRPApiClient(mock_aiohttp_session, "test_api_key")
        result = await client.login("test@example.com", "password123")

        assert result["session_id"] == "test_session_id_12345"
        assert len(result["vehicles"]) == 2
        assert result["vehicles"][0]["name"] == "Tesla Model 3"

    async def test_login_invalid_credentials(self, mock_aiohttp_session):
        """Test login with invalid credentials."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.raise_for_status = MagicMock(
            side_effect=aiohttp.ClientResponseError(
                request_info=MagicMock(),
                history=(),
                status=401,
            )
        )

        mock_aiohttp_session.post = AsyncMock(
            return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
        )

        client = ABRPApiClient(mock_aiohttp_session, "test_api_key")

        with pytest.raises(InvalidAuth):
            await client.login("test@example.com", "wrongpassword")

    async def test_login_connection_error(self, mock_aiohttp_session):
        """Test login with connection error."""
        mock_aiohttp_session.post = AsyncMock(
            side_effect=aiohttp.ClientError("Connection failed")
        )

        client = ABRPApiClient(mock_aiohttp_session, "test_api_key")

        with pytest.raises(CannotConnect):
            await client.login("test@example.com", "password123")

    async def test_get_telemetry_success(
        self, mock_aiohttp_session, mock_telemetry_response
    ):
        """Test successful telemetry fetch."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_telemetry_response)
        mock_response.raise_for_status = MagicMock()

        mock_aiohttp_session.post = AsyncMock(
            return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
        )

        client = ABRPApiClient(mock_aiohttp_session, "test_api_key")
        result = await client.get_telemetry("test_session_id", "12345")

        assert "tlm" in result
        assert result["tlm"]["soc"] == 85
        assert result["tlm"]["speed"] == 65

    async def test_get_telemetry_without_vehicle_id(
        self, mock_aiohttp_session, mock_telemetry_response
    ):
        """Test telemetry fetch without vehicle ID."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_telemetry_response)
        mock_response.raise_for_status = MagicMock()

        mock_aiohttp_session.post = AsyncMock(
            return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
        )

        client = ABRPApiClient(mock_aiohttp_session, "test_api_key")
        result = await client.get_telemetry("test_session_id")

        assert "tlm" in result

    async def test_extract_session_info_with_various_formats(
        self, mock_aiohttp_session
    ):
        """Test session info extraction with different response formats."""
        client = ABRPApiClient(mock_aiohttp_session, "test_api_key")

        # Test with session_id key
        result = await client._extract_session_info(
            {"session_id": "abc123", "vehicles": [{"id": "v1", "name": "Car 1"}]}
        )
        assert result["session_id"] == "abc123"
        assert len(result["vehicles"]) == 1

        # Test with sessionId key (camelCase)
        result = await client._extract_session_info(
            {"sessionId": "def456", "vehicles": []}
        )
        assert result["session_id"] == "def456"

        # Test with nested session.id
        result = await client._extract_session_info(
            {"session": {"id": "ghi789"}, "vehicles": []}
        )
        assert result["session_id"] == "ghi789"

        # Test with token key
        result = await client._extract_session_info(
            {"token": "jkl012", "vehicles": []}
        )
        assert result["session_id"] == "jkl012"

    async def test_extract_session_info_missing_session(self, mock_aiohttp_session):
        """Test session info extraction when session ID is missing."""
        client = ABRPApiClient(mock_aiohttp_session, "test_api_key")

        with pytest.raises(InvalidAuth):
            await client._extract_session_info({"vehicles": []})


@pytest.mark.integration
class TestABRPApiClientIntegration:
    """Integration tests for ABRP API client (requires real credentials)."""

    async def test_real_login(
        self, enable_integration_tests, test_email, test_password, test_api_key
    ):
        """Test login with real credentials from .env file."""
        if not enable_integration_tests:
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=true")

        async with aiohttp.ClientSession() as session:
            client = ABRPApiClient(session, test_api_key)

            result = await client.login(test_email, test_password)

            assert "session_id" in result
            assert isinstance(result["session_id"], str)
            assert len(result["session_id"]) > 0
            assert "vehicles" in result
            assert isinstance(result["vehicles"], list)

            print(f"\nLogin successful!")
            print(f"Session ID: {result['session_id']}")
            print(f"Found {len(result['vehicles'])} vehicles")
            for vehicle in result["vehicles"]:
                print(f"  - {vehicle['name']} (ID: {vehicle['id']})")

    async def test_real_telemetry(
        self,
        enable_integration_tests,
        test_email,
        test_password,
        test_api_key,
        test_vehicle_id,
    ):
        """Test telemetry fetch with real credentials."""
        if not enable_integration_tests:
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=true")

        async with aiohttp.ClientSession() as session:
            client = ABRPApiClient(session, test_api_key)

            # First login to get session ID
            login_result = await client.login(test_email, test_password)
            session_id = login_result["session_id"]

            # Use provided vehicle ID or first from login
            vehicle_id = test_vehicle_id
            if not vehicle_id and login_result["vehicles"]:
                vehicle_id = login_result["vehicles"][0]["id"]

            # Fetch telemetry
            telemetry = await client.get_telemetry(session_id, vehicle_id)

            assert telemetry is not None
            print(f"\nTelemetry data retrieved successfully:")
            if "tlm" in telemetry:
                tlm = telemetry["tlm"]
                print(f"  SOC: {tlm.get('soc')}%")
                print(f"  Speed: {tlm.get('speed')} km/h")
                print(f"  Location: {tlm.get('latitude')}, {tlm.get('longitude')}")
                print(f"  Charging: {tlm.get('is_charging')}")
            else:
                print(f"  Raw response: {telemetry}")

    async def test_real_login_invalid_credentials(self, test_api_key):
        """Test login with invalid credentials."""
        async with aiohttp.ClientSession() as session:
            client = ABRPApiClient(session, test_api_key)

            with pytest.raises((InvalidAuth, CannotConnect)):
                await client.login("invalid@example.com", "wrongpassword")
