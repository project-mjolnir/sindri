#!/usr/bin/env python3
"""
Basic processing code for HAMMA Mjolnir data.
"""

# Standard library imports
from pathlib import Path

# Third party imports
import pandas as pd

# Local imports
import sindri.utils.misc


DATA_DIR_DEFAULT = Path.home() / "data" / "monitoring"
GLOB_PATTERN_DEFAULT = "hamma*_????-??-??.csv"

FIGSIZE_DEFAULT = (8, 24)

CALCULATED_COLUMNS = (
    ("power_load", "power_out",
     lambda full_data: full_data["adc_vl_f"] * full_data["adc_il_f"]),
    ("trigger_delta", None,
     (lambda full_data: round(
         -1 * full_data["bytes_remaining"].diff(1)
         / (sindri.utils.misc.TRIGGER_SIZE_MB * 1e6)).clip(lower=0))),
    ("trigger_rate_1min", None,
     lambda full_data: full_data["trigger_delta"]
     / round(full_data["time"].diff(1).dt.total_seconds() / 60)),
    ("trigger_rate_5min", None,
     lambda full_data:
     full_data["trigger_delta"].rolling(5, min_periods=1).mean()
     / round(full_data["time"].diff(5).dt.total_seconds() / (60 * 5))),
    ("trigger_rate_1hr", None,
     lambda full_data:
     full_data["trigger_delta"].rolling(60, min_periods=1).mean()
     / round(full_data["time"].diff(60).dt.total_seconds() / (60 * 60))),
    ("triggers_remaining", None,
     lambda full_data: round(full_data["bytes_remaining"]
                             / (1e6 * sindri.utils.misc.TRIGGER_SIZE_MB))),
    ("crc_errors_delta", None,
     lambda full_data: full_data["crc_errors"].diff(1).clip(lower=0)),
    ("crc_errors_hourly", None,
     lambda full_data: full_data["crc_errors_delta"].last("1H").sum()),
    ("crc_errors_daily", None,
     lambda full_data: full_data["crc_errors_delta"].last("24H").sum()),
    ("sensor_uptime", None,
     lambda full_data: full_data["sequence_count"] / (60 * 60)),
    )


def get_status_data_paths(n_days=None, lag=None, data_dir=DATA_DIR_DEFAULT,
                          glob_pattern=GLOB_PATTERN_DEFAULT):
    files_to_load = Path(data_dir).glob(glob_pattern)
    if n_days is not None:
        if lag:
            files_to_load = sorted(
                list(files_to_load))[(-1 * n_days - lag):(lag * -1)]
        else:
            files_to_load = sorted(list(files_to_load))[-1 * n_days:]
    return files_to_load


def load_status_data(n_days=None, lag=None, data_dir=DATA_DIR_DEFAULT,
                     glob_pattern=GLOB_PATTERN_DEFAULT):
    files_to_load = get_status_data_paths(
        n_days=n_days, lag=lag, data_dir=data_dir, glob_pattern=glob_pattern)
    status_data = pd.concat(
        [pd.read_csv(file) for file in files_to_load], ignore_index=True)
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
    status_data["time"] = pd.to_datetime(status_data["time"])
    status_data["timestamp"] = pd.to_datetime(status_data["timestamp"])
    status_data.set_index("time", drop=False, inplace=True)

    status_data = calculate_columns(
        status_data, column_specs=column_specs)

    return status_data


def ingest_status_data(n_days=None, lag=0, decimate=None):
    raw_status_data = load_status_data(n_days=n_days, lag=lag)
    status_data = preprocess_status_data(raw_status_data, decimate=decimate)
    return status_data


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
    plot_status_data(ingest_status_data(n_days=7))
