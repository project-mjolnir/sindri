#!/usr/bin/env python3
"""
Setup script for Sindri.
"""

from pathlib import Path

import setuptools


PROJECT_NAME = "sindri"
PACKAGE_DIR = "src"
WEBSITE_TEMPLATE_SUBPATH = Path(
    "website", "mjolnir-website", "themes", "lektor-icon")
WEBSITE_TEMPLATE_EXCLUDE_GLOBS = [
    "nppBackup/*", "*.orig", "*.bak", "*.tmp", "*.md", "*.ttf", "bootstrap.css"
    ]
WEBSITE_TEMPLATE_EXCLUDE_SUBPATHS = [
    "images", "example-site"]

# Get project dir path
project_dir = Path(__file__).resolve().parent

# Get readme description
with open(project_dir / "README.md",
          "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

# Single-source version number
version = {}
with open(project_dir
          / "src" / PROJECT_NAME / "_version.py",
          "r", encoding="utf-8") as version_file:
    exec(version_file.read(), version)

# Build a list of data files in site theme
package_path = Path(project_dir, PACKAGE_DIR, PROJECT_NAME)
website_template_exclude_paths_full = [
    (WEBSITE_TEMPLATE_SUBPATH / subpath)
    for subpath in WEBSITE_TEMPLATE_EXCLUDE_SUBPATHS]
website_template_base = package_path / "website" / "mjolnir-website"
website_template_files = website_template_base.glob("**/*")
website_template_files = [file_path.relative_to(package_path)
                          for file_path in website_template_files]
website_template_files = [
    file_path for file_path in website_template_files if not any(
        [file_path.match(exclude_path)
         for exclude_path in WEBSITE_TEMPLATE_EXCLUDE_GLOBS] +
        [parent_path in file_path.parents
         for parent_path in website_template_exclude_paths_full])]


setuptools.setup(
    name=PROJECT_NAME,
    version=version["__version__"],
    author="C.A.M. Gerlach/UAH HAMMA group",
    author_email="CAM.Gerlach@Gerlach.CAM",
    description=("Receive, process, monitor, store and serve data from "
                 "scientific IoT sensors. Part of the Mjolnir system."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="iot lightning sensor remote control research m2m server web",
    url="https://www.hamma.dev/",
    packages=setuptools.find_packages(PACKAGE_DIR),
    package_dir={"": PACKAGE_DIR},
    package_data={
        PROJECT_NAME: [
            file_path.as_posix() for file_path in website_template_files],
        },
    python_requires=">=3.6",
    install_requires=[
        "brokkr>=0.4.0",
        "jinja2>=2,<3",
        "lektor>=3.1.3,<4",
        "MarkupSafe>=1,<2",
        "numpy>=1,<2",
        "pandas>=1,<2",
        "serviceinstaller>=0.2.0; sys_platform == 'linux'",
        ],
    entry_points={
        "console_scripts": [
            f"{PROJECT_NAME}={PROJECT_NAME}.__main__:main",
            ],
        },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Environment :: No Input/Output (Daemon)",
        "Framework :: Lektor",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: System :: Monitoring",
        ],
    )
