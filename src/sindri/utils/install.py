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
    log_kwargs = {"stream": sys.stdout, "format": "{message}", "style": "{"}
    if verbose is None:
        log_kwargs["level"] = 99
    elif verbose:
        log_kwargs["level"] = "DEBUG"
        log_kwargs["format"] = "{levelname} | {name} | {message}"
    else:
        log_kwargs["level"] = "INFO"
    logging.basicConfig(**log_kwargs)


def install_sindri_service(
        mode="client",
        account=None,
        extra_args="",
        verbose=None,
        **serviceinstaller_args,
        ):
    log_setup(verbose)

    service_config = copy.deepcopy(sindri.config.service.SERVICE_CONFIG[mode])
    settings = service_config["service_settings"]["Service"]

    if extra_args:
        settings["ExecStart"] = settings["ExecStart"] + " " + extra_args
    if account:
        settings["User"] = account

    serviceinstaller.install_service(**service_config, **serviceinstaller_args)


if __name__ == "__main__":
    install_sindri_service()
