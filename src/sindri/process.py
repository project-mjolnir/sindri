#!/usr/bin/env python3
"""
Basic processing code for HAMMA Mjolnir data.
"""

# Standard library imports
import warnings
from pathlib import Path

# Third party imports
import pandas as pd

# Local imports
import sindri.utils.misc


DATA_DIR_CLIENT = Path.home() / "brokkr" / "hamma" / "telemetry"
GLOB_PATTERN_CLIENT = "telemetry_hamma_???_????-??-??.csv"

DATA_DIR_SERVER = Path("/") / "var" / "www" / "hamma.dev" / "public_html"
GLOB_PATTERN_SUBDIR = "hamma[0-9]*"
DATA_SUBDIR_SERVER = Path() / "daily"
GLOB_PATTERN_SERVER = "hamma*_????-??-??.csv"

FIGSIZE_DEFAULT = (8, 24)

POWER_IDLE_W = 2.8

CALCULATED_COLUMNS = (
    ("power_load", "power_out",
     lambda full_data: full_data["adc_vl_f"] * full_data["adc_il_f"]),
    ("power_net", "power_load",
     lambda full_data:
         (full_data["power_out"] - full_data["power_load"] - POWER_IDLE_W)),
    ("ahnet_daily", "ahl_daily",
     lambda full_data:
         (full_data["ahc_daily"] - full_data["ahl_daily"])),
    ("sensor_uptime", "vb_max",
     lambda full_data: full_data["sequence_count"] / (60 * 60)),
    ("crc_errors_delta", "crc_errors",
     lambda full_data: full_data["crc_errors"].diff(1).clip(lower=0)),
    ("crc_errors_hourly", "crc_errors_delta",
     lambda full_data:
         full_data["crc_errors_delta"].rolling(60, min_periods=2).sum()
         / (round(full_data["time"].diff(60).dt.total_seconds()) / (60 * 60))),
    ("crc_errors_daily", "crc_errors_hourly",
     lambda full_data:
         full_data["crc_errors_delta"].rolling(60 * 24, min_periods=2).sum()
         / (round(full_data["time"].diff(60 * 24).dt.total_seconds())
            / (60 * 60 * 24))),
    ("trigger_delta", "valid_packets",
     (lambda full_data: round(
         -1e3 * full_data["bytes_remaining"].diff(1)
         / sindri.utils.misc.TRIGGER_SIZE_MB).clip(lower=0))),
    ("trigger_rate_1min", "trigger_delta",
     lambda full_data: full_data["trigger_delta"]
     / (round(full_data["time"].diff(1).dt.total_seconds()) / 60)),
    ("trigger_rate_5min", "trigger_rate_1min",
     lambda full_data:
     full_data["trigger_delta"].rolling(5, min_periods=2).mean()
     / (round(full_data["time"].diff(5).dt.total_seconds()) / (60 * 5))),
    ("trigger_rate_1hr", "trigger_rate_5min",
     lambda full_data:
     full_data["trigger_delta"].rolling(60, min_periods=6).mean()
     / (round(full_data["time"].diff(60).dt.total_seconds()) / (60 * 60))),
    ("triggers_remaining", "bytes_remaining",
     lambda full_data: round(full_data["bytes_remaining"] * 1e3
                             / sindri.utils.misc.TRIGGER_SIZE_MB)),
    )


def get_status_data_paths(
        n_days=None,
        lag=None,
        data_dir=DATA_DIR_CLIENT,
        glob_pattern=GLOB_PATTERN_CLIENT,
        ):

    files_to_load = sorted(list(Path(data_dir).glob(glob_pattern)))
    if n_days is not None:
        if lag:
            files_to_load = files_to_load[(-1 * n_days - lag):(lag * -1)]
        else:
            files_to_load = files_to_load[-1 * n_days:]
    return files_to_load


def get_status_data_paths_bykey(
        n_days=None,
        data_dir=DATA_DIR_SERVER,
        glob_subdir=GLOB_PATTERN_SUBDIR,
        data_subdir=DATA_SUBDIR_SERVER,
        glob_pattern=GLOB_PATTERN_SERVER,
        **path_kwargs,
        ):
    paths_byunit = {}
    for unit_dir in data_dir.glob(glob_subdir):
        data_paths = get_status_data_paths(
            n_days=n_days,
            data_dir=unit_dir / data_subdir,
            glob_pattern=glob_pattern,
            **path_kwargs,
            )
        if data_paths:
            paths_byunit[unit_dir.stem] = data_paths
    return paths_byunit


def get_all_status_data_subpaths(**path_kwargs):
    paths_bykey = get_status_data_paths_bykey(**path_kwargs)
    return sorted([path for paths in paths_bykey.values() for path in paths])


def load_status_data(n_days=None, lag=None, data_dir=DATA_DIR_CLIENT,
                     glob_pattern=GLOB_PATTERN_CLIENT):
    files_to_load = get_status_data_paths(
        n_days=n_days, lag=lag, data_dir=data_dir, glob_pattern=glob_pattern)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        status_data = pd.concat(
            (pd.read_csv(file, error_bad_lines=False)
             for file in files_to_load),
            ignore_index=True, sort=False)
    return status_data


def calculate_columns(df, column_specs=CALCULATED_COLUMNS):
    for colname, after_col, col_function in column_specs:
        if after_col:
            insert_location = df.columns.get_loc(after_col) + 1
        else:
            insert_location = len(df.columns)
        df.insert(insert_location, colname, col_function(df))
    return df


def preprocess_status_data(raw_status_data, decimate=None,
                           column_specs=CALCULATED_COLUMNS):
    if decimate:
        status_data = raw_status_data.iloc[::decimate, :]
    else:
        status_data = raw_status_data
    status_data["time"] = pd.to_datetime(
        status_data["time"],
        format="%Y-%m-%d %H:%M:%S.%f").dt.tz_localize(None)
    status_data.set_index("time", drop=False, inplace=True)
    status_data = status_data[status_data.index.notnull()]

    if column_specs:
        status_data = calculate_columns(status_data, column_specs=column_specs)

    return status_data


def ingest_status_data_client(
        n_days=None, data_dir=DATA_DIR_CLIENT, lag=0, decimate=None):
    raw_status_data = load_status_data(
        n_days=n_days, data_dir=data_dir, lag=lag)
    status_data = preprocess_status_data(raw_status_data, decimate=decimate)
    return status_data


def ingest_status_data_server(n_days=None, data_dir=DATA_DIR_SERVER):
    status_data_units = {}
    for unit_dir in data_dir.glob(GLOB_PATTERN_SUBDIR):
        try:
            raw_status_data = load_status_data(
                n_days=n_days,
                data_dir=unit_dir / DATA_SUBDIR_SERVER,
                glob_pattern=GLOB_PATTERN_SERVER,
                )
            status_data = preprocess_status_data(
                raw_status_data, column_specs=())
        except Exception as error:
            print(f"Error loading status data at {unit_dir.as_posix()!r}")
            print(f"{type(error).__name__}: {error}")
            continue

        status_data_units[unit_dir.stem] = status_data
    return status_data_units


def plot_status_data(
        status_data,
        save_path=None,
        columns_to_plot=None,
        figsize=FIGSIZE_DEFAULT,
        ):
    # Import here to avoid requiring matplotlib
    import pandas.plotting
    import matplotlib.pyplot as plt

    pandas.plotting.register_matplotlib_converters()
    if columns_to_plot is None:
        columns_to_plot = status_data.columns
    figure, axes = plt.subplots(len(columns_to_plot), 1, sharex=True,
                                figsize=figsize, dpi=100)
    for col_name, ax in zip(columns_to_plot, axes):
        ax.plot(status_data.index, status_data[col_name])
        ax.set_title(col_name, loc="left", pad=-10)

    figure.tight_layout()
    plt.subplots_adjust(hspace=0)

    if save_path:
        plt.savefig(save_path, dpi=100, bbox="tight", pad_inches=0.1)
    return figure, axes


if __name__ == "__main__":
    plot_status_data(ingest_status_data_client(n_days=7))
