"""Constants for the Zyxel integration."""
from datetime import timedelta

DOMAIN = "zyxel_dx54c"
PLATFORMS = ["device_tracker", "sensor"]
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 600
UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
CONF_SCAN_INTERVAL = "scan_interval"
