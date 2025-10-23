"""Fixtures for ABRP tests."""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dotenv import load_dotenv

from homeassistant.core import HomeAssistant

# Load test credentials from .env file
load_dotenv()


@pytest.fixture
def test_email():
    """Return test email from environment."""
    return os.getenv("ABRP_EMAIL", "test@example.com")


@pytest.fixture
def test_password():
    """Return test password from environment."""
    return os.getenv("ABRP_PASSWORD", "testpassword")


@pytest.fixture
def test_api_key():
    """Return test API key from environment."""
    return os.getenv("ABRP_API_KEY", "f4128c06-5e39-4852-95f9-3286712a9f3a")


@pytest.fixture
def test_session_id():
    """Return test session ID from environment."""
    return os.getenv(
        "ABRP_SESSION_ID", "13cc54e2c8c72fa98f19787961774cdc8ebc5a30f3b42798"
    )


@pytest.fixture
def test_vehicle_id():
    """Return test vehicle ID from environment."""
    return os.getenv("ABRP_VEHICLE_ID", "535799763889")


@pytest.fixture
def mock_aiohttp_session():
    """Return a mocked aiohttp session."""
    session = MagicMock()
    return session


@pytest.fixture
def mock_login_response():
    """Return mock successful login response."""
    return {
        "session_id": "test_session_id_12345",
        "vehicles": [
            {"id": "12345", "name": "Tesla Model 3"},
            {"id": "67890", "name": "Nissan Leaf"},
        ],
    }


@pytest.fixture
def mock_telemetry_response():
    """Return mock telemetry response."""
    return {
        "tlm": {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 65,
            "soc": 85,
            "power": -15.5,
            "is_charging": 0,
            "voltage": 385.2,
            "current": -40.3,
            "ext_temp": 22,
            "batt_temp": 28,
            "soh": 98,
            "est_battery_range": 320,
            "elevation": 150,
            "car_model": "tesla:m3:19:bt37:awd",
            "utc": 1234567890,
            "location": {
                "weather": {
                    "temp": 22,
                    "humidity": 65,
                    "wind_speed": 5.5,
                    "wind_deg": 180,
                    "pressure": 1013,
                    "description": "clear sky",
                    "clouds": 10,
                }
            },
        }
    }


@pytest.fixture
def hass():
    """Return a mock Home Assistant instance."""
    hass_mock = MagicMock(spec=HomeAssistant)
    hass_mock.data = {}
    hass_mock.config_entries = MagicMock()
    return hass_mock


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "email": "test@example.com",
        "api_key": "test_api_key",
        "session_id": "test_session_id",
        "vehicle_id": "12345",
    }
    return entry


@pytest.fixture
def enable_integration_tests():
    """Check if integration tests should run (requires real credentials)."""
    return all(
        [
            os.getenv("ABRP_EMAIL"),
            os.getenv("ABRP_PASSWORD"),
            os.getenv("RUN_INTEGRATION_TESTS") == "true",
        ]
    )
