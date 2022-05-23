"""
Load the configuration for the plots and tables on the generated website.
"""

# Standard library imports
import copy
from pathlib import Path

# Third party imports
from brokkr.config.systempath import SYSTEMPATH_CONFIG
import brokkr.utils.misc


# Module-level constants needed to find and load website config

WEBSITE_CONFIG_SUBDIR = "website"
DEFAULT_DASHBOARD = "main"
DASHBOARD_SUFFIX = ".py"
CONTENT_VAR_NAME = "CONTENT_PAGES"
MODE_VAR_NAME = "MODE"

SYSTEM_PATH = brokkr.utils.misc.get_system_path(SYSTEMPATH_CONFIG)
WEBSITE_CONFIG_PATH = SYSTEM_PATH / WEBSITE_CONFIG_SUBDIR


def load_website_config(
        dashboard=None, dashboard_dir=WEBSITE_CONFIG_PATH, mode=None):
    # Set up path to selected dashboard
    dashboard = dashboard or DEFAULT_DASHBOARD
    dashboard_path = Path(dashboard_dir) / dashboard
    if not dashboard_path.suffix:
        dashboard_path = dashboard_path.with_suffix(DASHBOARD_SUFFIX)

    # Set up namespace
    dashboard_config = {}
    if mode is not None:
        dashboard_config[MODE_VAR_NAME] = mode

    # Load dashboard configuration
    with open(dashboard_path, encoding="UTF-8") as dashboard_config_file:
        exec(dashboard_config_file.read(), dashboard_config)

    return dashboard_config


_website_config = load_website_config()


# Config settings loaded from website config

DATA_DIR_CLIENT = _website_config["DATA_DIR_CLIENT"]
GLOB_PATTERN_CLIENT = _website_config["GLOB_PATTERN_CLIENT"]

DATA_DIR_SERVER = _website_config["DATA_DIR_SERVER"]
GLOB_PATTERN_SUBDIR = _website_config["GLOB_PATTERN_SUBDIR"]
DATA_SUBDIR_SERVER = _website_config["DATA_SUBDIR_SERVER"]
GLOB_PATTERN_SERVER = _website_config["GLOB_PATTERN_SERVER"]

OUTPUT_DIR_SERVER = _website_config["OUTPUT_DIR_SERVER"]
OUTPUT_TARGET_CLIENT = _website_config.get("OUTPUT_TARGET_CLIENT", None)


DATETIME_COLNAME = _website_config.get("DATETIME_COLNAME", "time")
DATETIME_FORMAT = _website_config.get(
    "DATETIME_FORMAT", "%Y-%m-%d %H:%M:%S.%f")

CALCULATED_COLUMNS = _website_config.get("CALCULATED_COLUMNS", ())


CONTENT_PAGES_CLIENT = copy.deepcopy(_website_config["CONTENT_PAGES_CLIENT"])
CONTENT_PAGES_SERVER = copy.deepcopy(_website_config["CONTENT_PAGES_SERVER"])


def get_content_config(mode):
    if mode in {"test", "client"}:
        return copy.deepcopy(CONTENT_PAGES_CLIENT)
    else:
        return copy.deepcopy(CONTENT_PAGES_SERVER)
