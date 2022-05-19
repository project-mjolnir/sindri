"""
Load the configuration for the plots and tables on the generated website.
"""

# Standard library imports
from pathlib import Path

# Third party imports
from brokkr.config.systempath import SYSTEMPATH_CONFIG
import brokkr.utils.misc


DASHBOARDS_SUBDIR = "website"
DEFAULT_DASHBOARD = "main"
DASHBOARD_SUFFIX = ".py"
CONTENT_VAR_NAME = "CONTENT_PAGES"
MODE_VAR_NAME = "MODE"

SYSTEM_PATH = brokkr.utils.misc.get_system_path(SYSTEMPATH_CONFIG)
DASHBOARDS_PATH = SYSTEM_PATH / DASHBOARDS_SUBDIR


def load_dashboard_full_config(
        dashboard=None, dashboard_dir=DASHBOARDS_PATH, mode=None):
    # Set up path to selected dashboard
    dashboard = dashboard or DEFAULT_DASHBOARD
    dashboard_path = Path(dashboard_dir) / dashboard
    if not dashboard_path.suffix:
        dashboard_path = dashboard_path.with_suffix(DASHBOARD_SUFFIX)

    # Set up namespace
    dashboard_config_namespace = {}
    if mode is not None:
        dashboard_config_namespace[MODE_VAR_NAME] = mode

    # Load dashboard configuration
    with open(dashboard_path, encoding="UTF-8") as dashboard_config:
        exec(dashboard_config.read(), dashboard_config_namespace)

    return dashboard_config_namespace


def load_dashboard_content_config(**load_kwargs):
    full_config = load_dashboard_full_config(**load_kwargs)
    return full_config[CONTENT_VAR_NAME]
