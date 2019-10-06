"""
Utility functions for Sindri.
"""

# Standard library imports
from pathlib import Path
import os
import sys


PACKAGE_NAME = "Sindri"


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
