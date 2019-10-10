"""
Data, plots and calculations for the HAMMA Mjolnir status website.
"""

# Standard library imports
import copy
import json
import math
from pathlib import Path
import time

# Local imports
import sindri.templates
from sindri.utils import WEBSITE_UPDATE_FREQUENCY_S as UPDATE_FREQ


STATUS_JSON_PATH = Path("status_data.json")

STATUS_UPDATE_INTERVAL_SECONDS = 10
STATUS_UPDATE_INTERVAL_FAST_SECONDS = 1


STATUS_DATA_ARGS_DEFAULT = {
    "delta_period": "1H",
    "overlay_functions": (),
    "threshold_period": "24H",
    "threshold_type": "min",
    }


STATUS_DASHBOARD_PLOTS = {
    "weblatency": {
        "plot_type": None,
        "plot_data": {},
        "plot_metadata": {
            "plot_title": "Website Latency",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": 0,
            "plot_mode": "gauge+number+delta",
            "delta_reference": 0,
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": UPDATE_FREQ // 2,
            "range": [0, UPDATE_FREQ * 2],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0, UPDATE_FREQ], "green"),
                ([UPDATE_FREQ, UPDATE_FREQ + 60], "yellow"),
                ([UPDATE_FREQ + 60, UPDATE_FREQ + 3 * 60], "orange"),
                ([UPDATE_FREQ + 3 * 60, 4320000], "red"),
                )),
            "threshold_value": UPDATE_FREQ,
            "number_color": "white",
            "number_suffix": " s",
            "plot_update_code": (
                "data['value'] = (new Date() "
                "- lastUpdate) / (1000);\n"
                f"data['delta.reference'] = {UPDATE_FREQ};\n"
                + sindri.templates.GAUGE_PLOT_UPDATE_CODE_COLOR
                ),
            },
        "fast_update": True,
        },
    "battvoltage": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "min",
            "variable": "adc_vb_f",
            },
        "plot_metadata": {
            "plot_title": "Battery Voltage",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": 0,
            "plot_mode": "gauge+number+delta",
            "delta_reference": 0,
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 1,
            "range": [10, 15],
            "tick0": 9,
            "steps": sindri.templates.generate_step_string((
                ([0.00, 10.4], "red"),
                ([10.4, 11.0], "orange"),
                ([11.0, 12.0], "yellow"),
                ([12.0, 14.2], "green"),
                ([14.2, 14.6], "yellow"),
                ([14.6, 14.9], "orange"),
                ([14.9, 99.9], "red"),
                )),
            "threshold_value": 13.1,
            "number_color": "white",
            "number_suffix": " V",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    }


def safe_nan(value):
    if math.isnan(value):
        return -999
    return value


def get_plot_data(plot_type=None, **kwargs):
    if not plot_type:
        return None

    data_args = copy.deepcopy(STATUS_DATA_ARGS_DEFAULT)
    data_args.update(**kwargs)
    full_data = sindri.plot.load_status_data(latest_n=2)

    plot_data = []
    if plot_type == "numeric":
        if callable(data_args["variable"]):
            base_data = data_args["variable"](full_data)
        else:
            base_data = full_data.loc[:, data_args["variable"]]
        data_functions = (
            (lambda full_data: base_data.iloc[-1]),
            (lambda full__data:
             base_data.last(data_args["delta_period"]).iloc[0]),
            (lambda full_data: base_data.last(data_args["threshold_period"])),
            )

        if data_args["overlay_functions"]:
            overlay_functions = data_args["overlay_functions"]
        else:
            overlay_functions = [lambda value: value for __ in range(2)]
            if data_args["threshold_type"] == "min":
                overlay_functions.append(lambda val: min(val))
            elif data_args["threshold_type"] == "max":
                overlay_functions.append(lambda val: max(val))
            elif data_args["threshold_type"] == "mean":
                overlay_functions.append(lambda val: sum(val) / len(val))
            else:
                raise ValueError(
                    "Either overlay_functions must be defined or "
                    "threshold_type must be one of {'min', 'max', 'mean'} "
                    "with plot_type 'numeric', not "
                    + str(data_args['threshold_type'])
                    )

    elif plot_type == "custom":
        data_functions = data_args["data_functions"]
    else:
        raise ValueError("Plot type must be one of {None, 'numeric'}, not "
                         + str(plot_type))

    plot_data = tuple(safe_nan(overlay_function(data_function(full_data)))
                      for data_function, overlay_function
                      in zip(data_functions, overlay_functions))

    return plot_data


def generate_status_data(status_dashboard_plots=STATUS_DASHBOARD_PLOTS,
                         write_dir=None, write_path=STATUS_JSON_PATH):
    status_data = {
        plot_id:
            get_plot_data(plot_type=plot["plot_type"], **plot["plot_data"])
        for plot_id, plot in status_dashboard_plots.items()
        if plot["plot_type"]
        }
    status_data["lastupdatetimestamp"] = int(time.time() * 1000)
    if write_dir is not None and write_dir is not False and status_data:
        with open(Path(write_dir) / write_path, "w",
                  encoding="utf-8", newline="\n") as jsonfile:
            json.dump(status_data, jsonfile, separators=(",", ":"))
    return status_data


def generate_dashboard_block(
        status_dashboard_plots=STATUS_DASHBOARD_PLOTS,
        status_update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS,
        status_update_interval_fast_seconds=STATUS_UPDATE_INTERVAL_FAST_SECONDS
        ):
    widget_blocks = []
    all_plots = []
    fast_update_plots = []
    for plot_id, plot in status_dashboard_plots.items():
        widget_block = sindri.templates.DASHBOARD_ITEM_TEMPLATE.format(
            plot_id=plot_id, **plot["plot_metadata"])
        widget_blocks.append(widget_block)
        plot_setup = sindri.templates.DASHBOARD_PLOT_TEMPLATE.format(
            plot_id=plot_id, **plot["plot_params"])
        all_plots.append(plot_setup)
        if plot.get("fast_update", None):
            fast_update_plots.append(plot_id)
    widgets = "\n".join(widget_blocks)
    update_script = sindri.templates.DASHBOARD_SCRIPT_TEMPLATE.format(
        all_plots="\n".join(all_plots),
        status_json_path=STATUS_JSON_PATH,
        update_interval_s=status_update_interval_seconds,
        fast_update_plots=fast_update_plots,
        update_interval_fast_s=status_update_interval_fast_seconds,
        )
    dashboard_section = sindri.templates.DASHBOARD_SECTION_TEMPLATE.format(
        widgets=widgets, update_script=update_script)
    return dashboard_section


def generate_mainfile_content():
    mainfile_content = sindri.templates.MAINPAGE_SENSOR_TEMPLATE.format(
        main_content="\n".join((
            generate_dashboard_block(),
            )))
    return mainfile_content
