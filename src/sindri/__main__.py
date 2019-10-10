#!/usr/bin/env python3
"""
Main-level command handling routine for running Sindri on the command line.
"""

# Standard library imports
import argparse


def generate_argparser_main():
    parser_main = argparse.ArgumentParser(
        description="Server to recieve and process data from IoT sensors.",
        argument_default=argparse.SUPPRESS)
    parser_main.add_argument(
        "--version", action="store_true",
        help="If passed, will print the version and exit")
    subparsers = parser_main.add_subparsers(
        title="Subcommands", help="Subcommand to execute",
        metavar="Subcommand", dest="subcommand_name")

    # Parser for the version subcommand
    subparsers.add_parser(
        "version", help="Print Sindri's version, and then exit")

    # Parser for the help subcommand
    subparsers.add_parser(
        "help", help="Print help on Sindri's command line arguments")

    # Parser for the start subcommand
    parser_start = subparsers.add_parser(
        "start", help="Run Sindri as a continously updating service",
        argument_default=argparse.SUPPRESS)
    parser_start.add_argument(
        "--mode", type=str, choices=("test", "production"),
        help="Run Sindri in test or production mode")
    parser_start.add_argument(
        "-v", "--verbose", action="count", help="Increase verbosity of output")

    # Parser for the deploy-website subcommand
    parser_deploy = subparsers.add_parser(
        "deploy-website", help="Generate or deploy the status website",
        argument_default=argparse.SUPPRESS)
    parser_deploy.add_argument(
        "--mode", type=str, choices=("test", "production"),
        help="Run in test (local server) or production (build & deploy) mode")
    parser_deploy.add_argument(
        "-v", "--verbose", action="count", help="Increase verbosity of output")

    # Parser for the serve-website subcommand
    parser_serve = subparsers.add_parser(
        "serve-website", help="Run a continously updating website generator",
        argument_default=argparse.SUPPRESS)
    parser_serve.add_argument(
        "--mode", type=str, choices=("test", "production"),
        help="Run in test (local server) or production (build & deploy) mode")
    parser_serve.add_argument(
        "--update-frequency-s", type=float,
        help="Minimum update interval of the site, in seconds")
    parser_serve.add_argument(
        "-v", "--verbose", action="count", help="Increase verbosity of output")

    # Parser for the install-service subcommand
    parser_install_service = subparsers.add_parser(
        "install-service", help="Install Sindri as a systemd service (Linux)",
        argument_default=argparse.SUPPRESS)
    parser_install_service.add_argument(
        "--platform", choices=("linux", ),
        help="Manually override automatic platform detection")
    parser_install_service.add_argument(
        "-v", "--verbose", action="store_true",
        help="If passed, will print details of the exact actions executed")

    return parser_main


def main():
    parser_main = generate_argparser_main()
    parsed_args = parser_main.parse_args()
    subcommand = getattr(parsed_args, "subcommand_name", None)
    try:
        delattr(parsed_args, "subcommand_name")
    except Exception:  # Ignore any problem deleting the arg
        pass

    if getattr(parsed_args, "version", None) or subcommand == "version":
        import sindri
        print("Sindri version " + str(sindri.__version__))
    elif subcommand == "help":
        parser_main.print_help()
    elif subcommand == "start":
        import sindri.start
        sindri.start.start_sindri(**vars(parsed_args))
    elif subcommand == "deploy-website":
        import sindri.website.serve
        sindri.website.serve.deploy_website(**vars(parsed_args))
    elif subcommand == "serve-website":
        import sindri.website.serve
        sindri.website.serve.start_serving_website(**vars(parsed_args))
    elif subcommand == "install-service":
        import sindri.utils.install
        sindri.utils.install.install_sindri_service(**vars(parsed_args))
    else:
        parser_main.print_usage()


if __name__ == "__main__":
    main()
