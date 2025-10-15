# Testing Guide

This document explains how to run tests for the ABRP Home Assistant integration.

## Test Types

The integration includes two types of tests:

### 1. Unit Tests
- Mock all external API calls
- Fast execution
- No credentials required
- Test individual components in isolation

### 2. Integration Tests
- Use real ABRP API calls
- Require valid credentials
- Test actual authentication and data retrieval
- Verify real-world behavior

## Setup

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Configure Credentials (for Integration Tests)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your ABRP credentials:

```bash
# ABRP Account Credentials
ABRP_EMAIL=your-email@example.com
ABRP_PASSWORD=your-password

# Optional: Custom API Key (leave blank to use default)
ABRP_API_KEY=

# Optional: Known session ID for testing
ABRP_SESSION_ID=

# Optional: Known vehicle ID for testing
ABRP_VEHICLE_ID=

# Enable integration tests
RUN_INTEGRATION_TESTS=true
```

**⚠️ Security Note:** The `.env` file is git-ignored to prevent accidentally committing credentials.

## Running Tests

### Quick Start (Unit Tests Only)

```bash
./run_tests.sh
```

or

```bash
pytest -v -m unit tests/
```

### All Tests with Coverage

```bash
./run_tests.sh coverage
```

### Integration Tests Only

```bash
./run_tests.sh integration
```

or

```bash
pytest -v -m integration tests/
```

### Specific Test File

```bash
pytest tests/test_api.py -v
```

### Specific Test Function

```bash
pytest tests/test_api.py::TestABRPApiClientUnit::test_login_success -v
```

## Test Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Pytest fixtures and configuration
├── test_api.py              # API client tests
├── test_config_flow.py      # Configuration flow tests
└── test_init.py             # Integration setup tests
```

## Test Fixtures

Common fixtures available in all tests (from `conftest.py`):

- `test_email` - Test email from .env
- `test_password` - Test password from .env
- `test_api_key` - Test API key from .env
- `test_session_id` - Test session ID from .env
- `test_vehicle_id` - Test vehicle ID from .env
- `mock_aiohttp_session` - Mocked HTTP session
- `mock_login_response` - Mocked successful login response
- `mock_telemetry_response` - Mocked telemetry data
- `hass` - Mocked Home Assistant instance
- `enable_integration_tests` - Flag for integration tests

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.unit
async def test_login_success(mock_aiohttp_session, mock_login_response):
    """Test successful login with mocked response."""
    # Setup mock
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=mock_login_response)
    mock_aiohttp_session.post = AsyncMock(return_value=mock_response)

    # Test code here
    client = ABRPApiClient(mock_aiohttp_session, "test_key")
    result = await client.login("test@example.com", "password")

    assert result["session_id"] == "test_session_id_12345"
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
async def test_real_login(enable_integration_tests, test_email, test_password):
    """Test login with real credentials."""
    if not enable_integration_tests:
        pytest.skip("Integration tests disabled")

    async with aiohttp.ClientSession() as session:
        client = ABRPApiClient(session, "api_key")
        result = await client.login(test_email, test_password)

        assert "session_id" in result
        print(f"Session ID: {result['session_id']}")
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (mocked, fast)
- `@pytest.mark.integration` - Integration tests (real API calls)

## Coverage Reports

After running tests with coverage:

```bash
./run_tests.sh coverage
```

View the HTML report:

```bash
open htmlcov/index.html
```

## Continuous Integration

For CI/CD pipelines, run only unit tests:

```bash
pytest -v -m unit tests/
```

Integration tests should be run separately with credentials configured:

```bash
export ABRP_EMAIL="your-email@example.com"
export ABRP_PASSWORD="your-password"
export RUN_INTEGRATION_TESTS=true
pytest -v -m integration tests/
```

## Troubleshooting

### Import Errors

Make sure the integration is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Integration Tests Failing

1. Verify credentials in `.env` are correct
2. Check that `RUN_INTEGRATION_TESTS=true` is set
3. Ensure you have internet connectivity
4. Verify your ABRP account is active

### Async Test Issues

Make sure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

## Best Practices

1. **Always write unit tests** - They're fast and don't require credentials
2. **Use integration tests sparingly** - For critical paths and edge cases
3. **Mock external dependencies** - Use fixtures from `conftest.py`
4. **Test edge cases** - Invalid credentials, connection errors, etc.
5. **Keep tests isolated** - Each test should be independent
6. **Use descriptive names** - Test names should explain what they test

## Example Test Run Output

```
$ ./run_tests.sh
================================
ABRP Integration Test Runner
================================

📦 Installing test dependencies...
✅ Dependencies installed

🧪 Running all unit tests...
tests/test_api.py::TestABRPApiClientUnit::test_login_success PASSED
tests/test_api.py::TestABRPApiClientUnit::test_login_invalid_credentials PASSED
tests/test_config_flow.py::TestConfigFlowUnit::test_form_display PASSED
...

================================ 15 passed in 2.34s ================================

✅ Tests completed!
```
