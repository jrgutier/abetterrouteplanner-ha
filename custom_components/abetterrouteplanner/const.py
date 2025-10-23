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

# Sensor attributes (these map to keys in the ABRP telemetry data)
ATTR_LATITUDE = "lat"  # API uses 'lat', not 'latitude'
ATTR_LONGITUDE = "lon"  # API uses 'lon', not 'longitude'
ATTR_SPEED = "speed"
ATTR_SOC = "soc"
ATTR_SOE = "soe"  # State of Energy in kWh
ATTR_POWER = "power"
ATTR_IS_CHARGING = "is_charging"
ATTR_VOLTAGE = "voltage"
ATTR_CURRENT = "current"
ATTR_EXT_TEMP = "ext_temp"
ATTR_VEHICLE_TEMP = "vehicle_temp"
ATTR_BATT_TEMP = "batt_temp"
ATTR_CABIN_TEMP = "cabin_temp"
ATTR_EST_BATTERY_RANGE = "est_battery_range"
ATTR_BATTERY_CAPACITY = "battery_capacity"
ATTR_CAR_MODEL = "car_model"
ATTR_UTC = "utc"
ATTR_IS_PARKED = "is_parked"
ATTR_IS_DRIVING = "is_driving"
ATTR_HEADING = "heading"

# Weather attributes (from location.weather in telemetry)
ATTR_WEATHER_HUMIDITY = "weather_humidity"
ATTR_WEATHER_WIND_SPEED = "weather_wind_speed"
ATTR_WEATHER_WIND_DEG = "weather_wind_deg"
ATTR_WEATHER_PRESSURE = "weather_pressure"
ATTR_WEATHER_DESCRIPTION = "weather_description"
ATTR_WEATHER_CLOUDS = "weather_clouds"
