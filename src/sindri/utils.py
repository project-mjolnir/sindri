"""
Utility functions for Sindri.
"""

# Standard library imports
import getpass
from pathlib import Path
import os
import stat
import sys
import time


PACKAGE_NAME = "Sindri"
WEBSITE_UPDATE_FREQUENCY_MIN = 6


def time_ns():
    # Fallback to non-ns time functions on Python <=3.6
    try:
        return time.time_ns()
    except AttributeError:
        return int(time.time()) * 1e9


def monotonic_ns():
    # Fallback to non-ns time functions on Python <=3.6
    try:
        return time.monotonic_ns()
    except AttributeError:
        return int(time.monotonic()) * 1e9


START_TIME = monotonic_ns()


def delay_until_desired_time(
        interval_minutes, start_time=START_TIME, sleep=1):
    next_time = (monotonic_ns() + interval_minutes * 60 * 1e9
                 - (monotonic_ns() - start_time)
                 % (interval_minutes * 60 * 1e9))
    while monotonic_ns() < next_time:
        time.sleep(
            min([sleep, (next_time - monotonic_ns()) / 1e9]))


def get_cache_dir():
    if os.name == "nt":
        appdata = os.environ.get("LOCALAPPDATA")
        if appdata is None:
            appdata = os.environ.get("APPDATA")
            if appdata is None:
                appdata = Path.home()
        cache_dir = Path(appdata) / PACKAGE_NAME / "Cache"
    elif sys.platform == "darwin":
        cache_dir = Path.home() / "Library" / "Caches" / PACKAGE_NAME
    else:
        cache_dir = (Path(os.environ.get("XDG_CACHE_HOME",
                                         Path.home() / ".cache"))
                     / PACKAGE_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_actual_home_dir():
    try:
        username = os.environ["SUDO_USER"]
    except KeyError:
        username = getpass.getuser()
    return Path("~" + username).expanduser()


def force_delete(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)
