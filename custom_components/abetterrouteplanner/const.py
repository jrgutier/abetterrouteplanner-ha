"""Constants for the A Better Route Planner integration."""

DOMAIN = "abetterrouteplanner"

# Configuration
CONF_API_KEY = "api_key"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_SESSION_ID = "session_id"
CONF_VEHICLE_ID = "vehicle_id"
CONF_VEHICLES = "vehicles"

DEFAULT_NAME = "ABRP"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_API_KEY = "f4128c06-5e39-4852-95f9-3286712a9f3a"

# API
API_BASE_URL = "https://api.iternio.com/1"
API_TELEMETRY_ENDPOINT = "/session/get_tlm"
API_AUTH_ENDPOINT = "/auth/login"

# Sensor attributes
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"
ATTR_SPEED = "speed"
ATTR_SOC = "soc"
ATTR_POWER = "power"
ATTR_IS_CHARGING = "is_charging"
ATTR_VOLTAGE = "voltage"
ATTR_CURRENT = "current"
ATTR_EXT_TEMP = "ext_temp"
ATTR_BATT_TEMP = "batt_temp"
ATTR_SOH = "soh"
ATTR_EST_BATTERY_RANGE = "est_battery_range"
ATTR_ELEVATION = "elevation"
ATTR_CAR_MODEL = "car_model"
ATTR_UTC = "utc"
