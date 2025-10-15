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

1. **Get your ABRP Session ID** (see below)
2. Go to **Settings** → **Devices & Services** in Home Assistant
3. Click **+ Add Integration**
4. Search for "A Better Route Planner"
5. Enter your configuration:
   - **Session ID**: Your ABRP session ID (required)
   - **Vehicle ID**: Optional - leave blank to monitor all vehicles
   - **API Key**: Leave as default unless you have a custom API key
6. Done! Your sensors will appear automatically

### Getting Your ABRP Session ID

Since ABRP uses reCAPTCHA protection, you need to extract your session ID from the browser:

1. **Log in** to [A Better Route Planner](https://abetterrouteplanner.com) in your browser
2. **Open Developer Tools** (F12 or Right-click → Inspect)
3. Go to the **Network** tab
4. **Refresh the page** or navigate in ABRP
5. Look for a request to `api.iternio.com` containing `/session/`
6. Click on the request and view the **Request Payload**
7. Copy the `session_id` value (it's a long string like `37c4267efee530df5ba2933f8117edb5607a59f92df9073`)
8. Optionally, copy the `wakeup_vehicle_id` if you want to monitor a specific vehicle

**Example Request Payload:**
```json
{
  "session_id": "37c4267efee530df5ba2933f8117edb5607a59f92df9073",
  "wakeup_vehicle_id": 535799763889
}
```

### How It Works

The integration:
- Uses your session ID to authenticate with ABRP
- Fetches telemetry data every 30 seconds
- Creates 15+ sensors for vehicle data
- Works with all vehicles in your ABRP account

**Note:** Session IDs may expire after extended periods of inactivity. If sensors stop updating, simply obtain a new session ID from your browser and update the integration configuration.

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
