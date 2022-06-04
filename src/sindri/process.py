#!/usr/bin/env python3
"""
Data ingest and processing code for Mjolnir (and other) data.
"""

# Standard library imports
from pathlib import Path

# Third party imports
import importlib_metadata
import packaging.version
import pandas as pd

# Local imports
from sindri.config.website import (
    CALCULATED_COLUMNS,
    DATA_DIR_CLIENT,
    DATA_DIR_SERVER,
    DATA_SUBDIR_SERVER,
    DATETIME_COLNAME,
    DATETIME_FORMAT,
    GLOB_PATTERN_CLIENT,
    GLOB_PATTERN_SERVER,
    UNIT_DIRS_SERVER,
    )


FIGSIZE_DEFAULT = (8, 24)


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
        unit_dirs=UNIT_DIRS_SERVER,
        data_subdir=DATA_SUBDIR_SERVER,
        glob_pattern=GLOB_PATTERN_SERVER,
        **path_kwargs,
        ):
    paths_byunit = {}
    for unit_dir in unit_dirs:
        data_paths = get_status_data_paths(
            n_days=n_days,
            data_dir=data_dir / unit_dir / data_subdir,
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

    pandas_ver = packaging.version.parse(importlib_metadata.version("pandas"))
    if pandas_ver < packaging.version.parse("1.3.0"):
        read_csv_kwargs = {"error_bad_lines": False, "warn_bad_lines": True}
    else:
        read_csv_kwargs = {"on_bad_lines": "warn"}

    status_data = pd.concat(
        (pd.read_csv(file, **read_csv_kwargs) for file in files_to_load),
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


def preprocess_status_data(
        raw_status_data, decimate=None, column_specs=CALCULATED_COLUMNS):
    if decimate:
        status_data = raw_status_data.iloc[::decimate, :]
    else:
        status_data = raw_status_data
    status_data[DATETIME_COLNAME] = pd.to_datetime(
        status_data[DATETIME_COLNAME],
        format=DATETIME_FORMAT,
        ).dt.tz_localize(None)
    status_data.set_index(DATETIME_COLNAME, drop=False, inplace=True)
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


def ingest_status_data_server(
        n_days=None, data_dir=DATA_DIR_SERVER, unit_dirs=UNIT_DIRS_SERVER):
    status_data_units = {}
    for unit_dir in unit_dirs:
        data_subdir = data_dir / unit_dir / DATA_SUBDIR_SERVER
        try:
            raw_status_data = load_status_data(
                n_days=n_days,
                data_dir=data_subdir,
                glob_pattern=GLOB_PATTERN_SERVER,
                )
            status_data = preprocess_status_data(
                raw_status_data, column_specs=())
        except Exception as error:
            print(f"Error loading status data at {data_subdir.as_posix()!r}")
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
