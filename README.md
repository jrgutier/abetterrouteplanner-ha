# A Better Route Planner (ABRP) Integration for Home Assistant

This integration allows you to monitor your vehicle's telemetry data from [A Better Route Planner](https://abetterrouteplanner.com) in Home Assistant.

## Features

- Real-time vehicle telemetry monitoring
- 15+ sensors including:
  - State of Charge (%)
  - Speed
  - Location (latitude/longitude)
  - Charging status
  - Power usage
  - Battery temperature
  - External temperature
  - Voltage and current
  - State of Health
  - Estimated battery range
  - And more!

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Search for "A Better Route Planner" in HACS
3. Click "Install"
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/abetterrouteplanner` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Quick Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "A Better Route Planner"
4. Sign in with your ABRP credentials:
   - **Email**: Your ABRP account email
   - **Password**: Your ABRP account password
   - **API Key** (optional): Leave as default unless you have a custom API key
5. If you have multiple vehicles, select which one to monitor
6. Done! Your sensors will appear automatically

### How It Works

The integration automatically:
- Logs into your ABRP account
- Retrieves your session ID
- Discovers all vehicles associated with your account
- Fetches telemetry data every 30 seconds

No need to manually extract session IDs or API keys from browser developer tools!

## Development

This integration includes a VS Code devcontainer for easy development.

### Prerequisites

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- Visual Studio Code
- Remote - Containers extension for VS Code

### Setup

1. Clone this repository
2. Open the folder in VS Code
3. When prompted, click "Reopen in Container"
4. Wait for the container to build and start
5. The integration will be automatically loaded in the development Home Assistant instance

### Testing

Access the development Home Assistant instance at http://localhost:9123

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/jrgutier/abetterrouteplanner-ha/issues).

## License

This project is licensed under the MIT License.
