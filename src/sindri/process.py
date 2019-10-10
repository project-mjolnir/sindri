#!/usr/bin/env python3
"""
Basic processing code for HAMMA Mjolnir data.
"""

# Standard library imports
from pathlib import Path


# Third party imports
import pandas as pd
import pandas.plotting
import matplotlib.pyplot as plt


DATA_PATH_DEFAULT = Path.home() / "data" / "monitoring"
GLOB_PATTERN_DEFAULT = "hamma*_????-??-??.csv"

FIGSIZE_DEFAULT = (8, 24)


def load_status_data(
        latest_n=None,
        decimate=None,
        data_path=DATA_PATH_DEFAULT,
        glob_pattern=GLOB_PATTERN_DEFAULT,
        ):
    # Load
    files_to_load = Path(data_path).glob(glob_pattern)
    if latest_n is not None:
        files_to_load = sorted(list(files_to_load))[-1 * latest_n:]
    status_data = pd.concat(
        (pd.read_csv(file) for file in files_to_load), ignore_index=True)

    # Convert values
    if decimate:
        status_data = status_data.iloc[::decimate, :]
    status_data["time"] = pd.to_datetime(status_data["time"])
    status_data["timestamp"] = pd.to_datetime(status_data["timestamp"])
    status_data.set_index("time", drop=False, inplace=True)

    return status_data


def plot_status_data(
        status_data,
        save_path=None,
        columns_to_plot=None,
        figsize=FIGSIZE_DEFAULT,
        ):
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
    test_data = load_status_data(latest_n=7)
    plot_status_data(test_data)
