#!/usr/bin/env python3
"""
Main-level command handling routine for running Sindri on the command line.
"""

# Standard library imports
import argparse


MODE_NAMES = ("test", "client", "server")


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

    parsers_add_mode_arg = []
    parsers_add_update_interval_arg = []
    parsers_add_temp_cache_arg = []
    parsers_add_dest_arg = []
    parsers_add_verbose_arg = []

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
    parsers_add_mode_arg.append(parser_start)
    parsers_add_update_interval_arg.append(parser_start)
    parsers_add_dest_arg.append(parser_start)
    parsers_add_verbose_arg.append(parser_start)

    # Parser for the deploy-website subcommand
    parser_deploy = subparsers.add_parser(
        "deploy-website", help="Generate or deploy the status website",
        argument_default=argparse.SUPPRESS)
    parsers_add_mode_arg.append(parser_deploy)
    parsers_add_temp_cache_arg.append(parser_deploy)
    parsers_add_dest_arg.append(parser_deploy)
    parsers_add_verbose_arg.append(parser_deploy)

    # Parser for the serve-website subcommand
    parser_serve = subparsers.add_parser(
        "serve-website", help="Run a continously updating website generator",
        argument_default=argparse.SUPPRESS)
    parsers_add_mode_arg.append(parser_serve)
    parsers_add_update_interval_arg.append(parser_serve)
    parsers_add_temp_cache_arg.append(parser_serve)
    parsers_add_dest_arg.append(parser_serve)
    parsers_add_verbose_arg.append(parser_serve)

    # Parser for the install-service subcommand
    parser_install_service = subparsers.add_parser(
        "install-service", help="Install Sindri as a systemd service (Linux)",
        argument_default=argparse.SUPPRESS)
    parser_install_service.add_argument(
        "--platform", choices=("linux", ),
        help="Manually override automatic platform detection")
    parser_install_service.add_argument(
        "--extra-args", help="Extra args ")
    parsers_add_mode_arg.append(parser_install_service)
    parsers_add_verbose_arg.append(parser_install_service)

    # Add common args
    for parser in parsers_add_mode_arg:
        parser.add_argument(
            "--mode", type=str, choices=MODE_NAMES,
            help="Run in test, client (Pi-side) or server (VPS-side) mode")
    for parser in parsers_add_update_interval_arg:
        parser.add_argument(
            "--update-interval-s", type=float,
            help="Minimum update interval of the site, in seconds")
    for parser in parsers_add_temp_cache_arg:
        parser.add_argument(
            "--temp-cache-dir", dest="cache_dir",
            nargs="?", default=None, const=True,
            help=(
                "If passed with a path, will use it as the source cache dir "
                "for the site. If passed alone, will use the temp cache dir "
                "instead of the primary one (useful for serving a site locally"
                " on-demand simultantiously with a production site). "
                "If not passed, will use the default primary cache dir."
                )),
    for parser in parsers_add_dest_arg:
        parser.add_argument(
            "--dest-dir", help="Path to which to copy the site build output")
    for parser in parsers_add_verbose_arg:
        parser.add_argument(
            "-v", "--verbose", action="count", help="Increase verbosity")

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
