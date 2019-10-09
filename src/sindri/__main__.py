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

    # Parser for the website subcommand
    parser_website = subparsers.add_parser(
        "generate-website", help="Generate or deploy the status website",
        argument_default=argparse.SUPPRESS)
    parser_website.add_argument(
        "--mode", type=str, choices=("test", "production"),
        help="Run in test (local server) or production (build & deploy) mode")
    parser_website.add_argument(
        "-v", "--verbose", action="count", help="Increase verbosity of output")

    # Parser for the webserver subcommand
    parser_website = subparsers.add_parser(
        "webserver", help="Run a continously updating static site generator",
        argument_default=argparse.SUPPRESS)
    parser_website.add_argument(
        "--update-frequency-min", type=float,
        help="Minimum update interval of the site, in minutes")
    parser_website.add_argument(
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
    elif subcommand == "generate-website":
        import sindri.website
        sindri.website.generate_website(**vars(parsed_args))
    elif subcommand == "webserver":
        import sindri.website
        sindri.website.start_serving_website(**vars(parsed_args))
    elif subcommand == "install-service":
        import sindri.install
        sindri.install.install_sindri_service(**vars(parsed_args))
    else:
        parser_main.print_usage()


if __name__ == "__main__":
    main()
