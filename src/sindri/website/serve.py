"""
Code to generate, build and deploy the Mjolnir status website.
"""

# Standard library imports
import configparser
from pathlib import Path
import shutil
import subprocess
import sys
import time

# Local imports
import sindri.config.website
import sindri.utils.misc
import sindri.website.generate


LEKTOR_SOURCE_DIR = "mjolnir-website"
LEKTOR_SOURCE_PATH = Path(__file__).parent / LEKTOR_SOURCE_DIR
LEKTOR_PROJECT_PATH = (
    sindri.utils.misc.get_cache_dir() / "main" / LEKTOR_SOURCE_DIR)
LEKTOR_PROJECT_FILENAME = "mjolnir-website.lektorproject"
LEKTOR_DEFAULT_SERVER_NAME = "mjolnir"

SOURCE_IGNORE_PATTERNS = (
    "temp", "*.tmp", "*.temp", "*.bak", "*.log", "*.orig", "example-site")


def get_website_cache_dir(cache_dir=None):
    if cache_dir is None:
        return LEKTOR_PROJECT_PATH
    elif cache_dir is True:
        return sindri.utils.misc.get_cache_dir() / "temp" / LEKTOR_SOURCE_DIR
    elif cache_dir is False:
        return Path() / "Sindri_Website_Source_Cache" / LEKTOR_SOURCE_DIR
    else:
        return Path(cache_dir)


def render_lektorproject(
        project_name=None, project_path=LEKTOR_PROJECT_PATH):
    if project_name is None:
        project_filename = LEKTOR_PROJECT_FILENAME
    else:
        project_filename = f"{project_name}.lektorproject"

    project_config = configparser.ConfigParser()
    project_config.read(project_path / project_filename, encoding="UTF-8")
    project_config.read(
        sindri.config.website.WEBSITE_CONFIG_PATH / project_filename,
        encoding="UTF-8")

    server_section = f"servers.{LEKTOR_DEFAULT_SERVER_NAME}"
    if (project_config.has_section(server_section)
            and not project_config.has_option(server_section, "target")
            and sindri.config.website.OUTPUT_TARGET_CLIENT
            ):
        project_config[server_section]["target"] = (
            sindri.config.website.OUTPUT_TARGET_CLIENT)

    return project_config


def update_data(project_path=LEKTOR_PROJECT_PATH, mode="test"):
    sindri.website.generate.generate_site_data(
        content_pages=sindri.config.website.get_content_config(mode=mode),
        project_path=project_path,
        mode=mode,
        )


def update_project(project_path=LEKTOR_PROJECT_PATH, mode="test"):
    update_data(project_path=project_path, mode=mode)
    sindri.website.generate.generate_and_write_site_content(
        content_pages=sindri.config.website.get_content_config(mode=mode),
        project_path=project_path,
        )


def rebuild_project(
        source_path=LEKTOR_SOURCE_PATH,
        output_path=LEKTOR_PROJECT_PATH,
        mode=None,
        ):
    try:
        shutil.rmtree(output_path, onerror=sindri.utils.misc.force_delete)
    except Exception:
        pass
    sindri.utils.misc.copytree(
        source_path, output_path, ignore_patterns=SOURCE_IGNORE_PATTERNS)

    lektorproject_config = render_lektorproject(project_path=output_path)
    with open(output_path / LEKTOR_PROJECT_FILENAME, "w",
              encoding="utf-8", newline="\n") as lektorproject_file:
        lektorproject_config.write(lektorproject_file)

    update_project(project_path=output_path, mode=mode)


def run_lektor(command, args=(), project_path=LEKTOR_PROJECT_PATH, verbose=1):
    extra_args = {}
    lektor_call = [sys.executable, "-m", "lektor", command, *args]
    if verbose <= 0:
        extra_args = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    elif verbose >= 2 and command in {"server", "build"}:
        lektor_call.append("-v")

    if command == "server":
        return subprocess.Popen(
            lektor_call, cwd=project_path, **extra_args)
    else:
        return subprocess.run(
            lektor_call, check=True, cwd=project_path, **extra_args)


def build_deploy_lektor(mode, cache_dir, dest_dir=None, verbose=0):
    if mode == "server" and dest_dir is None:
        dest_dir = sindri.config.website.OUTPUT_DIR_SERVER
    run_lektor(command="build", project_path=cache_dir, verbose=verbose + 1)
    if dest_dir:
        build_dir_output = run_lektor(
            "project-info",
            args=["--output-path"],
            project_path=cache_dir,
            verbose=0,
            )
        build_dir = Path(build_dir_output.stdout.decode().strip())
        sindri.utils.misc.copytree(build_dir, dest_dir)
    if mode == "client":
        run_lektor(command="deploy", project_path=cache_dir, verbose=verbose)


def deploy_website(
        mode="test",
        cache_dir=None,
        dest_dir=None,
        wait_exit=True,
        verbose=0,
        ):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    cache_dir = get_website_cache_dir(cache_dir)
    rebuild_project(output_path=cache_dir, mode=mode)

    if mode == "test":
        run_lektor(command="server", project_path=cache_dir,
                   verbose=verbose + 1)
        if wait_exit:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Keyboard interrupt recieved; exiting.")
    elif mode in {"client", "server"}:
        build_deploy_lektor(
            mode=mode,
            cache_dir=cache_dir,
            dest_dir=dest_dir,
            verbose=verbose + 1,
            )


def start_serving_website(
        mode="test",
        update_interval_s=sindri.utils.misc.WEBSITE_UPDATE_INTERVAL_S,
        cache_dir=None,
        dest_dir=None,
        verbose=0,
        ):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    cache_dir = get_website_cache_dir(cache_dir)
    deploy_website(
        mode=mode,
        cache_dir=cache_dir,
        dest_dir=dest_dir,
        wait_exit=False,
        verbose=verbose,
        )

    try:
        # Initial 60 s wait to ensure site fully builds once before rerunning
        if mode == "test":
            for __ in range(58):
                time.sleep(1)
        while True:
            sindri.utils.misc.delay_until_desired_time(update_interval_s)
            update_data(project_path=cache_dir, mode=mode)
            if mode in {"client", "server"}:
                build_deploy_lektor(
                    mode=mode,
                    cache_dir=cache_dir,
                    dest_dir=dest_dir,
                    verbose=verbose,
                    )
    except KeyboardInterrupt:
        print("Keyboard interrupt recieved; exiting.")
