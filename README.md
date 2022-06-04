# Sindri

A Python package to process, serve and visualize data from scientific IoT sensors, typically from remote [Brokkr](https://github.com/project-mjolnir/brokkr) clients.
Part of [Project Mjolnir](https://github.com/project-mjolnir/), a system to allow remote monitoring, control and data uplink from multiple networks of scientific IoT sensors.

Currently, its primary functionality is to generate, render and serve extensively customizable, dynamically-generated real-time interactive web dashboards displaying telemetry and science data from sensors, both locally connected to the sensor, on remote machines and on the public web.


## License

Copyright (c) 2019-2022 C.A.M. Gerlach, the UAH HAMMA Group and the Project Mjolnir Contributors

This project is distributed under the terms of the MIT (Expat) License; see the [LICENSE.txt](./LICENSE.txt) for more details.



## Installation and Setup

Sindri is built and tested under Python 3.6-3.10, with a relatively minimal set of lightweight, pure-Python core dependencies.
It works best on Linux, but is tested to be fully functional (aside from service features) on Windows (and _should_ work equally on macOS) using the Anaconda distribution.


### Installation

On Linux (or other platforms, for experienced users), Sindri can be installed like any other Python package, via ``pip`` into a ``venv`` virtual environment.

For example, with the venv created inside ``ENV_DIR`` in the current working directory:

```shell
python3 -m venv ENV_DIR
source ENV_DIR/bin/activate
pip install sindri
```

On Windows and Mac, use of Anaconda/Miniconda is recommended, substituting conda environments for venvs.
Those platforms are fully supported, with the exception of built-in support for running as an OS-native system service.

Additionally, you'll need to install ``imagemagick`` separately, due to a dependency needed by the site generator.
To do so, you can typically simply run (with ``sudo``, if required):

```shell
PACKAGE_MANAGER install imagemagick
```

where ``PACKAGE_MANAGER`` is ``conda`` if you have it, or otherwise your system package manager of choice (``apt``, ``dnf``, ``yum``, ``brew``, ``choco``, etc).


### Setup

Now that Sindri sources its configuration from a Mjolnir system config package, you'll need to take a few more steps to get your environment set up.
Specifically, you'll need to clone the system config package(s) you want to use with Sindri (replace the example ``mjolnir-config-template`` path with yours), and use Brokkr to register them, and set up your config and unit information, if you haven't already.
To do so, run the following, where ``SYSTEM_SHORTNAME`` is whatever name you want to register the system with in the system file, and ``UNIT_NUMBER`` is the integer number (arbitrary, but should be unique) you want to designate the device you're installing on (typically `0` for the central server):

```shell
git clone https://github.com/project-mjolnir/mjolnir-config-template.git
brokkr configure-system SYSTEM_SHORTNAME /path/to/system/mjolnir-config-template
brokkr configure-init
brokkr configure-unit UNIT_NUMBER
```

To run Sindri continuously with the selected system automatically on startup, you'll want to install it as a Systemd service with the ``sindri install-service`` subcommand.
This can be accomplished as follows, where ``MODE`` is the mode Sindri should run in (``client`` if directly on an individual sensor client, or ``server``) if on a central server recieving data from all the sensors:

```shell
sudo /PATH/TO/ENV_DIR/bin/python -m sindri install-service --mode MODE``
```

You can set a specific account, install path and startup arguments if desired; see ``brokkr install-service --help`` for more usage and option information.

Finally, you can check that Sindri is installed and set up correctly with ``sindri --version``, and there are a number of other commands useful for testing detailed in ``sindri --help``.

You can now start the ``sindri`` service you've installed with the usual

```shell
sudo systemctl start sindri-SYSTEM_SHORTNAME-MODE
```

or on all platforms you can run it manually with ``sindri start``, or the other invocation options mentioned in the help output.



## Usage

### Overview

See ``sindri --help`` and ``sindri <SUBCOMMAND> --help`` for detailed documentation of Sindri's CLI, invocation, options and subcommands.
The following is a brief, high-level summary.

For a quick check of Sindri, its version and that of the current system (if configured), use ``sindri --version``.

Run the ``sindri deploy-website --mode MODE`` command to deploy the website once in ``MODE`` mode as a snapshot of the monitoring data, to check its status.
The ``test`` mode starts a local webserver at ``http://localhost:5000`` (``http://127.0.0.1:5000``) for previewing the results, and also optionally stays alive to update the site if you do so manually.
The production ``client`` and ``server`` mode deploys the site once to their respective configured deployment targets.

The ``sindri serve-website`` rebuilds and deploys the site continuously, either to a local webserver in ``test`` mode, or to the production deployment targets in ``client`` or ``server`` mode, updated in real time (every 1 s by default) as you watch.
``sindri start`` is the main entrypoint for Sindri's core functionality, which currently is essentially a wrapper around ``sindri serve-website``, and in normal usage is run though the Sindri service.

The ``sindri install-*`` commands perform installation functions, while ``brokr configure-*`` is used to  help set up a new or updated Mjolnir system install.

On Linux, the ``sindri-SYSTEMNAME-MODE`` systemd service can be interacted with via the standard systemd commands, e.g. ``sudo systemd {start, stop, enable, disable} sindri-SYSTEMNAME`-MODE`, ``systemd status sindri-SYSTEMNAME-MODE``, ``journalctl -u sindri-SYSTEMNAME-MODE``, etc.


### Interactive Use (Foreground)

First, activate the appropriate Python virtual environment (e.g. ``source ENV_DIR/bin/activate``).

Then, you have a few options:

* Main foreground start command, for testing: ``sindri start --mode MODE``
* Oneshot site deploy: ``sindri deploy-website --mode MODE``
* Realtime monitoring: ``sindri serve-website --mode MODE``


### Running Sindri as a Service (Background)

* Generate, install and enable service automatically:
    * ``sudo /home/pi/path/to/ENV_DIR/bin/python -m sindri install-service --mode MODE``
* Start/stop:
    * ``sudo systemctl start sindri-SYSTEMNAME-MODE``
    * ``sudo systemctl stop sindri-SYSTEMNAME-MODE``
* Enable/disable running on startup:
    * ``sudo systemctl enable sindri-SYSTEMNAME-MODE``
    * ``sudo systemctl disable sindri-SYSTEMNAME-MODE``
* Basic status check and latest log output:
    * ``systemctl status sindri-SYSTEMNAME-MODE``
* Full log output:
    * ``journalctl -xe -u sindri-SYSTEMNAME-MODE``



## Configuration

A major design goal of Sindri and the Mjolnir system is extensive, flexible and straightforward reconfiguration for different sensor networks and changing needs.
For example, with the UAH HAMMA2 system, all the system configuration is normally handled through the [Mjolnir-HAMMA system config package](https://github.com/hamma-dev/mjolnir-hamma/) in the standard Mjolnir config schema developed for this system, aside from a few high-level elements specific to each unit which all have interactive configuration commands as below.

However, if local customization is needed beyond the high-level options specified here, instead of modifying the version-control-tracked system config package directly, the config system built for this is fully hierarchical and all settings can be fully overridden via the corresponding local config in ``~/.config/brokkr/SYSTEM_NAME``.
Sindri fully supports configuration, logging, operation and output of any number of Mjolnir systems simultaneously, all on the same Pi or server.

Configuration files are located under the XDG-standard ``~/.config/brokkr`` directory in the ini-like [TOML](https://github.com/toml-lang/toml) format; they can be generated by running ``brokkr configure-init`` (which will not overwrite them if they already exist), and reset to defaults with ``brokkr configure-reset``.


### High-level local setting configuration

#### Register, update and remove systems

Register a Mjolnir system:

```shell
brokkr configure-system <SYSTEM-NAME> </PATH/TO/SYSTEM/CONFIG/DIR>
```

(e.g. ``brokkr configure-system hamma /home/pi/dev/mjolnir-hamma``)

You can also use this command to remove, update, verify and set default systems with the appropriate arguments; see ``brokkr configure-system --help``


#### Generate local config files

Generate empty local per-system (i.e. override) config files if not already present:

```shell
brokkr configure-init
```

#### Set per-unit configuration

```shell
brokkr configure-unit <UNIT_NUMBER>
```

(e.g. ``brokkr configure-unit 1 --network-interface wlan0``)


#### Reset configuration

Reset unit and local override configuration (optionally minus the system registry):

```shell
brokkr configure-reset
```
