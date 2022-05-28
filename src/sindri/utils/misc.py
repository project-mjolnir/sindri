"""
Utility functions for Sindri.
"""

# Standard library imports
import getpass
from pathlib import Path
import os
import shutil
import stat
import sys
import time


PACKAGE_NAME = "Sindri"
WEBSITE_UPDATE_INTERVAL_S = 60
TRIGGER_SIZE_MB = 22.0


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
        interval_seconds, start_time=START_TIME, sleep=1):
    next_time = (monotonic_ns() + interval_seconds * 1e9
                 - (monotonic_ns() - start_time)
                 % (interval_seconds * 1e9))
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


def copytree(
        src,
        dst,
        ignore=None,
        copy_function=shutil.copyfile,
        ignore_patterns=None,
        ):
    source = Path(src).expanduser().resolve()
    destination = Path(dst).expanduser().resolve()
    if ignore is None and ignore_patterns is not None:
        ignore = shutil.ignore_patterns(*ignore_patterns)

    destination.mkdir(parents=True, exist_ok=True)

    dir_items = [item.relative_to(source) for item in source.iterdir()]
    if ignore:
        exclude_items = ignore(str(source), [str(item) for item in dir_items])
        dir_items = [
            item for item in dir_items if str(item) not in exclude_items]
    for item in dir_items:
        source_item = source / item
        destination_item = destination / item
        if source_item.is_dir():
            copytree(
                str(source_item),
                str(destination_item),
                ignore=ignore,
                copy_function=copy_function,
                )
        else:
            copy_function(source_item, destination_item)
