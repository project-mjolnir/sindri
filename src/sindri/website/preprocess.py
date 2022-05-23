"""
Utility functions for preprocessing the content config data for use.
"""

# Standard library imports
import copy

# Third party imports
import brokkr.utils.misc


DEFAULT_SUBPLOT_NAME = "DEFAULT"


def preprocess_subplot_params(plot, subplot_params, subplot_id=None):
    plot_params_default = {
        key: value for key, value in plot["plot_params"].items()
        if key not in {"subplots"}}

    subplot_params = brokkr.utils.misc.update_dict_recursive(
        plot_params_default, subplot_params, inplace=False)
    subplot_params["plot_data"] = {
        **plot.get("plot_data", {}),
        **subplot_params.get("plot_data", {}),
        }

    if subplot_id is not None:
        subplot_params["subplot_id"] = subplot_id
    for toplevel_param in {"plot_type", "fast_update"}:
        subplot_params[toplevel_param] = subplot_params.get(
            toplevel_param, plot.get(toplevel_param, None))

    defaults = {
        "subplot_title": "",
        "subplot_column": 0,
        "subplot_row": 0,
        "subplot_titlesize": 20,
        }
    subplot_params = {**defaults, **subplot_params}

    return subplot_params


def preprocess_subplots(plot):
    plot = copy.deepcopy(plot)
    subplots = plot["plot_params"].get("subplots", {DEFAULT_SUBPLOT_NAME: {}})
    subplots = {
        subplot_id: preprocess_subplot_params(plot, subplot_params, subplot_id)
        for subplot_id, subplot_params in subplots.items()}
    return subplots
