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
    parser_webserver = subparsers.add_parser(
        "webserver", help="Start the status website generator",
        argument_default=argparse.SUPPRESS)
    parser_webserver.add_argument(
        "--mode", type=str, choices=("test", "deploy", "production"),
        help=("Run in test (local server), deploy (oneshot build & deploy) "
              "or production (continous build & deploy) mode."))

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
    elif subcommand == "webserver":
        import sindri.website
        sindri.website.main(**vars(parsed_args))
    else:
        parser_main.print_usage()


if __name__ == "__main__":
    main()
