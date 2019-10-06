"""
Code to generate, build and deploy the HAMMA Mjolnir status website.
"""

# Standard library imports
from pathlib import Path
import shutil
import subprocess

# Local imports
import sindri.utils


LEKTOR_SOURCE_DIR = "mjolnir-website"
LEKTOR_SOURCE_PATH = Path(__file__).parent / LEKTOR_SOURCE_DIR
LEKTOR_PROJECT_PATH = sindri.utils.get_cache_dir() / LEKTOR_SOURCE_DIR

SOURCE_IGNORE_PATTERNS = (
    "temp", "*.tmp", "*.temp", "*.bak", "*.log", "*.orig", "example-site")


def process_data():
    import datetime
    return {"timestamp": datetime.datetime.now()}


def generate_sources(data, source_path=LEKTOR_SOURCE_PATH,
                     output_path=LEKTOR_PROJECT_PATH):
    data_towrite = {"status_data": f"Generation time: {data['timestamp']}"}
    mainpage_path = Path(output_path) / "content" / "contents.lr"

    shutil.rmtree(output_path, ignore_errors=True)
    shutil.copytree(source_path, output_path,
                    ignore=shutil.ignore_patterns(*SOURCE_IGNORE_PATTERNS))

    with open(mainpage_path, "r", encoding="utf-8", newline=None) as main_file:
        mainfile_content = main_file.read()
    mainfile_content = mainfile_content.format(**data_towrite)
    with open(mainpage_path, "w", encoding="utf-8", newline="\n") as main_file:
        main_file.write(mainfile_content)


def lektor_server(project_dir=LEKTOR_PROJECT_PATH):
    try:
        subprocess.run(("lektor", "server"), cwd=project_dir)
    except KeyboardInterrupt:
        print("Keyboard interrupt recieved; exiting.")


def lektor_build(project_dir=LEKTOR_PROJECT_PATH):
    subprocess.run(("lektor", "build"), check=True, cwd=project_dir)


def lektor_deploy(project_dir=LEKTOR_PROJECT_PATH):
    subprocess.run(("lektor", "deploy", "ghpages"),
                   check=True, cwd=project_dir)
    shutil.rmtree(Path(project_dir) / "temp", ignore_errors=True)


def serve_test():
    data = process_data()
    generate_sources(data=data)
    lektor_server()


def serve_deploy():
    data = process_data()
    generate_sources(data=data)
    lektor_build()
    lektor_deploy()


def serve_production():
    raise NotImplementedError("Production server not yet implemented.")


def main(mode="test"):
    # Fail fast if Lektor is not installed in the current environment
    import lektor
    if mode == "production":
        serve_production()
    elif mode == "deploy":
        serve_deploy()
    else:
        serve_test()


if __name__ == "__main__":
    main()
