"""
Code to generate, build and deploy the HAMMA Mjolnir status website.
"""

# Standard library imports
from pathlib import Path
import shutil
import subprocess
import sys

# Local imports
import sindri.plot
import sindri.templates
import sindri.utils
import sindri.websitedata


LEKTOR_SOURCE_DIR = "mjolnir-website"
LEKTOR_SOURCE_PATH = Path(__file__).parent / LEKTOR_SOURCE_DIR
LEKTOR_PROJECT_PATH = sindri.utils.get_cache_dir() / LEKTOR_SOURCE_DIR

SOURCE_IGNORE_PATTERNS = (
    "temp", "*.tmp", "*.temp", "*.bak", "*.log", "*.orig", "example-site")


def update_sources(project_path=LEKTOR_PROJECT_PATH):
    sindri.websitedata.generate_status_data(
        write_dir=project_path / sindri.templates.MAINPAGE_PATH.parent)

    with open(Path(project_path) / sindri.templates.MAINPAGE_PATH, "w",
              encoding="utf-8", newline="\n") as main_file:
        main_file.write(sindri.websitedata.generate_mainfile_content())


def generate_sources(source_path=LEKTOR_SOURCE_PATH,
                     output_path=LEKTOR_PROJECT_PATH):
    try:
        shutil.rmtree(output_path, onerror=sindri.utils.force_delete)
    except Exception:
        pass
    shutil.copytree(source_path, output_path,
                    ignore=shutil.ignore_patterns(*SOURCE_IGNORE_PATTERNS))
    update_sources(project_path=output_path)


def lektor_server(project_dir=LEKTOR_PROJECT_PATH, verbose=1):
    extra_args = {}
    lektor_server_call = [sys.executable, "-m", "lektor", "server"]
    if verbose == 0:
        extra_args = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    elif verbose >= 2:
        lektor_server_call.append("-v")
    try:
        subprocess.run(lektor_server_call, cwd=project_dir, **extra_args)
    except KeyboardInterrupt:
        print("Keyboard interrupt recieved; exiting.")


def lektor_build(project_dir=LEKTOR_PROJECT_PATH, verbose=1):
    extra_args = {}
    lektor_build_call = [sys.executable, "-m", "lektor", "build"]
    if verbose == 0:
        extra_args = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    elif verbose >= 2:
        lektor_build_call.append("-v")
    subprocess.run(lektor_build_call,
                   check=True, cwd=project_dir, **extra_args)


def lektor_deploy(project_dir=LEKTOR_PROJECT_PATH, verbose=1):
    extra_args = {}
    if verbose == 0:
        extra_args = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    subprocess.run([sys.executable, "-m", "lektor", "deploy", "ghpages"],
                   check=True, cwd=project_dir, **extra_args)


def generate_website_test(verbose=1):
    generate_sources()
    lektor_server(verbose=verbose)


def generate_website_production(verbose=1):
    generate_sources()
    lektor_build(verbose=verbose)
    lektor_deploy(verbose=verbose)


def generate_website(mode="test", verbose=0):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    if mode == "test":
        generate_website_test(verbose=verbose + 1)
    elif mode == "production":
        generate_website_production(verbose=verbose + 1)
    else:
        raise ValueError("Mode must be one of 'test' or 'production'.")


def start_serving_website(
        update_frequency_min=sindri.utils.WEBSITE_UPDATE_FREQUENCY_MIN,
        verbose=0):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    generate_website_production(verbose=verbose + 1)
    try:
        while True:
            sindri.utils.delay_until_desired_time(update_frequency_min)
            update_sources()
            lektor_build(verbose=verbose)
            lektor_deploy(verbose=verbose)
    except KeyboardInterrupt:
        print("Keyboard interrupt recieved; exiting.")
