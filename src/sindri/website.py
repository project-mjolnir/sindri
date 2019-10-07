"""
Code to generate, build and deploy the HAMMA Mjolnir status website.
"""

# Standard library imports
import datetime
from pathlib import Path
import os
import shutil
import stat
import subprocess
import time

# Third party imports
import pandas as pd

# Local imports
import sindri.plot
import sindri.utils


LEKTOR_SOURCE_DIR = "mjolnir-website"
LEKTOR_SOURCE_PATH = Path(__file__).parent / LEKTOR_SOURCE_DIR
LEKTOR_PROJECT_PATH = sindri.utils.get_cache_dir() / LEKTOR_SOURCE_DIR

SOURCE_IGNORE_PATTERNS = (
    "temp", "*.tmp", "*.temp", "*.bak", "*.log", "*.orig", "example-site")


def force_delete(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def process_data():
    status_data = sindri.plot.load_status_data(latest_n=8)
    return status_data


def generate_sources(data, source_path=LEKTOR_SOURCE_PATH,
                     output_path=LEKTOR_PROJECT_PATH):
    try:
        shutil.rmtree(output_path, onerror=force_delete)
    except Exception:
        pass
    shutil.copytree(source_path, output_path,
                    ignore=shutil.ignore_patterns(*SOURCE_IGNORE_PATTERNS))
    update_sources(data, project_path=output_path)


def update_sources(data, project_path=LEKTOR_PROJECT_PATH):
    image_location = "last_7_days.svg"
    mainpage_path = Path(project_path) / "content" / "contents.template"
    data_table_html = data.iloc[-1:, :].transpose().to_html()

    output_source = (f"Generation time: {datetime.datetime.now()}\n\n"
                     f"{data_table_html}\n\n"
                     f"![Status Plot]({image_location})")
    sindri.plot.plot_status_data(
        data.iloc[::15, :],
        project_path / "content" / image_location,
        figsize=(9, 24),
        )

    with open(mainpage_path, "r", encoding="utf-8", newline=None) as main_file:
        mainfile_content = main_file.read()
    mainfile_content = mainfile_content.format(status_data=output_source)
    with open(mainpage_path.with_suffix(".lr"),
              "w", encoding="utf-8", newline="\n") as main_file:
        main_file.write(mainfile_content)


def lektor_server(project_dir=LEKTOR_PROJECT_PATH, verbose=1):
    extra_args = {}
    lektor_server_call = ["lektor", "server"]
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
    lektor_build_call = ["lektor", "build"]
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
    subprocess.run(["lektor", "deploy", "ghpages"],
                   check=True, cwd=project_dir, **extra_args)


def generate_website_test(verbose=1):
    data = process_data()
    generate_sources(data=data)
    lektor_server(verbose=verbose)


def generate_website_production(verbose=1):
    data = process_data()
    generate_sources(data=data)
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


def delay_until_desired_time(
        interval_minutes, start_time=sindri.utils.START_TIME, sleep=1):
    next_time = (sindri.utils.monotonic_ns() + interval_minutes * 60 * 1e9
                 - (sindri.utils.monotonic_ns() - sindri.utils.START_TIME)
                 % (interval_minutes * 60 * 1e9))
    while sindri.utils.monotonic_ns() < next_time:
        time.sleep(
            min([sleep, (next_time - sindri.utils.monotonic_ns()) / 1e9]))


def start_serving_website(interval_minutes=5, verbose=0):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    generate_website_production(verbose=verbose + 1)
    try:
        while True:
            delay_until_desired_time(interval_minutes)
            data = process_data()
            update_sources(data=data)
            lektor_build(verbose=verbose)
            lektor_deploy(verbose=verbose)
    except KeyboardInterrupt:
        print("Keyboard interrupt recieved; exiting.")


if __name__ == "__main__":
    pass
    # start_serving_website()
