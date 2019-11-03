"""
Configuration to run Sindri as a service for supported platforms (Linux).
"""

# Standard library imports
import sys

# Local imports
import sindri.utils.misc

SERVICE_FILENAME = "sindri.service"
USER_HOME = sindri.utils.misc.get_actual_home_dir()

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
                        f"{str(USER_HOME / '.ssh' / 'id_rsa')}"),
        "ExecStart": f"{sys.executable} -m sindri start --mode 'production'",
        "Restart": "on-failure",
        "RestartSec": "300",
        "TimeoutStartSec": "300",
        "TimeoutStopSec": "300",
        },
    }

SERVICES_ENABLE = ("systemd-timesyncd.service", )
SERVICES_DISABLE = ("chronyd.service", "ntpd.service")
