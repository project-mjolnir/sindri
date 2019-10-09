"""
Configuration to run Sindri as a service for supported platforms (Linux).
"""

# Standard library imports
from pathlib import Path
import sys

# Local imports
import sindri.utils

SERVICE_FILENAME = "sindri.service"
USER_HOME = sindri.utils.get_actual_home_dir()

SERVICE_DEFAULTS = {
    "Unit": {
        "Description": "Sindri Server Service",
        "Wants": (
            "network-online.target systemd-time-wait-sync.service "
            "systemd-timesyncd.service"
            ),
        "After": (
            "time-sync.target network-online.target multi-user.target "
            "systemd-time-wait-sync.service systemd-timesyncd.service "
            "brokkr.service"
            ),
        },
    "Service": {
        "Type": "simple",
        "Environment": ("LEKTOR_DEPLOY_KEY_FILE="
                        f"{str(USER_HOME / '.ssh' / 'id_mjolnir')}"),
        "ExecStart": (
            f"{sys.executable} -m sindri webserver --update-frequency-min "
            f"{sindri.utils.WEBSITE_UPDATE_FREQUENCY_MIN}"
            ),
        "Restart": "on-failure",
        "RestartSec": str(360),
        "TimeoutStartSec": str(360),
        "TimeoutStopSec": str(360),
        },
    }

SERVICES_ENABLE = ("systemd-timesyncd.service", )
SERVICES_DISABLE = ("chronyd.service", "ntpd.service")
