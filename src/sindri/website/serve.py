"""
Code to generate, build and deploy the HAMMA Mjolnir status website.
"""

# Standard library imports
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
LEKTOR_PROJECT_PATH = sindri.utils.misc.get_cache_dir() / LEKTOR_SOURCE_DIR

SOURCE_IGNORE_PATTERNS = (
    "temp", "*.tmp", "*.temp", "*.bak", "*.log", "*.orig", "example-site")


def update_data(project_path=LEKTOR_PROJECT_PATH):
    sindri.website.generate.generate_site_data(
        content_pages=sindri.config.website.CONTENT_PAGES,
        project_path=project_path)


def update_project(project_path=LEKTOR_PROJECT_PATH):
    update_data(project_path=project_path)
    sindri.website.generate.generate_and_write_site_content(
        content_pages=sindri.config.website.CONTENT_PAGES,
        project_path=project_path)


def deploy_project(source_path=LEKTOR_SOURCE_PATH,
                   output_path=LEKTOR_PROJECT_PATH):
    try:
        shutil.rmtree(output_path, onerror=sindri.utils.misc.force_delete)
    except Exception:
        pass
    shutil.copytree(source_path, output_path,
                    ignore=shutil.ignore_patterns(*SOURCE_IGNORE_PATTERNS))
    update_project(project_path=output_path)


def run_lektor(command, project_dir=LEKTOR_PROJECT_PATH, verbose=1):
    extra_args = {}
    lektor_call = [sys.executable, "-m", "lektor", command]
    if verbose <= 0:
        extra_args = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    elif verbose >= 2 and command in {"server", "build"}:
        lektor_call.append("-v")

    if command == "server":
        subprocess.Popen(lektor_call, cwd=project_dir, **extra_args)
    else:
        subprocess.run(lektor_call, check=True,
                       cwd=project_dir, **extra_args)


def deploy_website(mode="test", verbose=0, wait_exit=True):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    deploy_project()
    if mode == "test":
        run_lektor(command="server", verbose=verbose + 1)
        if wait_exit:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Keyboard interrupt recieved; exiting.")
    elif mode == "production":
        run_lektor(command="build", verbose=verbose + 1)
        run_lektor(command="deploy ghpages", verbose=verbose + 1)


def start_serving_website(
        mode="test",
        update_interval_s=sindri.utils.misc.WEBSITE_UPDATE_INTERVAL_S,
        verbose=0,
        ):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    deploy_website(mode=mode, verbose=verbose, wait_exit=False)
    try:
        while True:
            sindri.utils.misc.delay_until_desired_time(update_interval_s)
            update_data()
            if mode == "production":
                run_lektor(command="build", verbose=verbose)
                run_lektor(command="deploy ghpages", verbose=verbose)
    except KeyboardInterrupt:
        print("Keyboard interrupt recieved; exiting.")
