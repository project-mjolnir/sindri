"""
Configuration to run Sindri as a service for supported platforms (Linux).
"""

# Standard library imports
import sys

# Third party imports
from brokkr.utils.services import (
    SERVICE_NAME_TEMPLATE,
    SYSTEM_FULLNAME,
    SYSTEM_NAME,
    SYSTEM_PARAMETER,
    )

# Local imports
import sindri.utils.misc


SERVICE_FILENAME_BASE = SERVICE_NAME_TEMPLATE.format(
    package_name="sindri", system_name=SYSTEM_NAME, mode="{mode}")
SERVICE_DESCRIPTION_BASE = (
    f"Sindri data visualization server for {SYSTEM_FULLNAME} ({{mode}} mode)")
EXEC_BASE = (
    f"{sys.executable} -m sindri {SYSTEM_PARAMETER} start --mode '{{mode}}'")

USER_HOME = sindri.utils.misc.get_actual_home_dir()


SERVICE_CONFIG = {
    "test": {
        "service_filename": SERVICE_FILENAME_BASE.format(mode="test"),
        "service_settings": {
            "Unit": {
                "Description": SERVICE_DESCRIPTION_BASE.format(mode="test"),
                "Wants": "systemd-time-wait-sync.service",
                "After": " ".join([
                    "time-sync.target",
                    "multi-user.target",
                    ]),
                },
            "Service": {
                "Type": "simple",
                "ExecStart": EXEC_BASE.format(mode="test"),
                },
            },
        "services_enable": (),
        "services_disable": (),
        },

    "client": {
        "service_filename": SERVICE_FILENAME_BASE.format(mode="client"),
        "service_settings": {
            "Unit": {
                "Description": SERVICE_DESCRIPTION_BASE.format(mode="client"),
                "Wants": (
                    "systemd-time-wait-sync.service"
                    ),
                "After": " ".join([
                    "time-sync.target",
                    "multi-user.target",
                    "systemd-time-wait-sync.service",
                    "systemd-timesyncd.service",
                    ]),
                },
            "Service": {
                "Type": "simple",
                "Environment": ("LEKTOR_DEPLOY_KEY_FILE="
                                f"{str(USER_HOME / '.ssh' / 'id_rsa')}"),
                "ExecStart": EXEC_BASE.format(mode="client"),
                "Restart": "on-failure",
                "RestartSec": "300",
                "TimeoutStartSec": "300",
                "TimeoutStopSec": "300",
                },
            },
        "services_enable": ("systemd-timesyncd.service", ),
        "services_disable": ("chronyd.service", "ntpd.service"),
        },

    "server": {
        "service_filename": SERVICE_FILENAME_BASE.format(mode="server"),
        "service_settings": {
            "Unit": {
                "Description": SERVICE_DESCRIPTION_BASE.format(mode="server"),
                "Wants": "systemd-time-wait-sync.service",
                "After": " ".join([
                    "time-sync.target",
                    "multi-user.target",
                    "systemd-time-wait-sync.service",
                    "systemd-timesyncd.service",
                    "chronyd.service",
                    "ntpd.service",
                    ]),
                },
            "Service": {
                "Type": "simple",
                "ExecStart": EXEC_BASE.format(mode="server"),
                "Restart": "on-failure",
                "RestartSec": "120",
                "TimeoutStartSec": "120",
                "TimeoutStopSec": "120",
                },
            },
        "services_enable": (),
        "services_disable": (),
        },
    }
