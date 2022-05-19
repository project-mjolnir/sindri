#!/usr/bin/env python3
"""
Install Sindri service and other items.
"""

# Standard library imports
import copy
import logging
import sys

# Third party imports
import serviceinstaller

# Local imports
import sindri.config.service


def log_setup(verbose=None):
    if verbose is None:
        logging_level = 99
    elif verbose:
        logging_level = "DEBUG"
    else:
        logging_level = "INFO"
    logging.basicConfig(stream=sys.stdout, level=logging_level)


def install_sindri_service(
        platform=None, mode="client", extra_args="", verbose=None):
    log_setup(verbose)

    service_config = copy.deepcopy(sindri.config.service.SERVICE_CONFIG[mode])
    if extra_args:
        settings = service_config["service_settings"]["Service"]
        settings["ExecStart"] = settings["ExecStart"] + " " + extra_args
    serviceinstaller.install_service(platform=platform, **service_config)


if __name__ == "__main__":
    install_sindri_service()
