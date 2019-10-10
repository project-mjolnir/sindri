"""
Data, plots and calculations for the HAMMA Mjolnir status website.
"""

# Standard library imports
import copy
import datetime
import json
import math
from pathlib import Path
import time

# Third party imports
import numpy as np

# Local imports
import sindri.plot
import sindri.templates
from sindri.utils import WEBSITE_UPDATE_FREQUENCY_S as UPDATE_FREQ


STATUS_JSON_PATH = Path("status_data.json")
SENTINEL_VALUE_JSON = -999

STATUS_UPDATE_INTERVAL_SECONDS = 10
STATUS_UPDATE_INTERVAL_FAST_SECONDS = 1

TRIGGER_SIZE_MB = 22.0


STATUS_DATA_ARGS_DEFAULT = {
    "data_functions": [
        lambda base_data, data_args: base_data.iloc[-1],
        lambda base_data, data_args: (
            base_data.last(data_args["delta_period"]).iloc[0]),
        lambda base_data, data_args: (
            base_data.last(data_args["threshold_period"])),
        ],
    "delta_period": "1H",
    "overlay_functions": [lambda value: value for __ in range(3)],
    "threshold_period": "24H",
    "threshold_type": None,
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
            "delta_reference": UPDATE_FREQ,
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": UPDATE_FREQ // 2,
            "range": [0, UPDATE_FREQ * 2],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0, UPDATE_FREQ], "green"),
                ([UPDATE_FREQ, UPDATE_FREQ + 60], "yellow"),
                ([UPDATE_FREQ + 60, UPDATE_FREQ + 3 * 60], "orange"),
                ([UPDATE_FREQ + 3 * 60, 32 * 24 * 60 * 60], "red"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " s",
            "plot_update_code": (
                "data['value'] = (new Date() "
                "- lastUpdate) / (1000);\n"
                "if (data['value'] > maxLatency) {\n"
                "    maxLatency = data['value'];\n"
                "    data['gauge.threshold.value'] = data['value'];\n"
                "};\n"
                + sindri.templates.GAUGE_PLOT_UPDATE_CODE_COLOR
                ),
            },
        "fast_update": True,
        },
    "datalatency": {
        "plot_type": "numeric",
        "plot_data": {
            "data_functions": (lambda base_data, data_args: base_data[-1], ),
            "variable": (lambda full_data:
                         (datetime.datetime.now() - full_data.index)
                         .total_seconds())
            },
        "plot_metadata": {
            "plot_title": "Data Latency",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": 60,
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": 60,
            "range": [0, 300],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0, 60], "green"),
                ([60, 120], "yellow"),
                ([120, 240], "orange"),
                ([240, 32 * 24 * 60 * 60], "red"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 60,
            "number_color": "white",
            "number_suffix": " s",
            "plot_update_code": (
                "\n".join((
                    *sindri.templates.GAUGE_PLOT_UPDATE_CODE_VALUE
                    .splitlines()[0:2],
                    sindri.templates.GAUGE_PLOT_UPDATE_CODE_COLOR
                    ))),
            },
        "fast_update": False,
        },
    "pinglatency": {
        "plot_type": "numeric",
        "plot_data": {
            "data_functions": (lambda base_data, data_args: base_data, ),
            "variable": (
                lambda full_data:
                (full_data.index[-1]
                 - full_data.loc[full_data["ping"] == 0, :].index[-1])
                .total_seconds())
            },
        "plot_metadata": {
            "plot_title": "Ping Latency",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": 60,
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": 60,
            "range": [0, 300],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0, 30], "green"),
                ([30, 90], "yellow"),
                ([90, 210], "orange"),
                ([210, 32 * 24 * 60 * 60], "red"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 60,
            "number_color": "white",
            "number_suffix": " s",
            "plot_update_code": (
                "\n".join((
                    *sindri.templates.GAUGE_PLOT_UPDATE_CODE_VALUE
                    .splitlines()[0:2],
                    sindri.templates.GAUGE_PLOT_UPDATE_CODE_COLOR
                    ))),
            },
        "fast_update": False,
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
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 1,
            "range": [10, 15],
            "tick0": 10,
            "steps": sindri.templates.generate_step_string((
                ([0.00, 10.4], "red"),
                ([10.4, 11.0], "orange"),
                ([11.0, 12.0], "yellow"),
                ([12.0, 14.2], "green"),
                ([14.2, 14.6], "yellow"),
                ([14.6, 14.9], "orange"),
                ([14.9, 99.9], "red"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " V",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "arrayvoltage": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": "adc_va_f",
            },
        "plot_metadata": {
            "plot_title": "Array Voltage",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 12,
            "range": [0, 60],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0.00, 4.00], "red"),
                ([2.00, 12.0], "orange"),
                ([12.0, 24.0], "yellow"),
                ([24.0, 60.0], "green"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " V",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "chargecurrent": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": "adc_ic_f",
            },
        "plot_metadata": {
            "plot_title": "Charging Current",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 2,
            "range": [0, 12],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0.0, 0.5], "red"),
                ([0.5, 1.0], "orange"),
                ([1.0, 2.5], "yellow"),
                ([2.0, 20.], "green"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " A",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "chargestate": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": "charge_state",
            },
        "plot_metadata": {
            "plot_title": "Charge State",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 1,
            "range": [0, 8],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0.0, 0.5], "gray"),
                ([0.5, 1.5], "blue"),
                ([1.5, 2.5], "red"),
                ([2.5, 3.5], "orange"),
                ([3.5, 4.5], "red"),
                ([4.5, 5.5], "yellow"),
                ([5.5, 6.5], "lime"),
                ([6.5, 7.5], "green"),
                ([7.5, 8.5], "teal"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "loadpower": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "min",
            "variable": (lambda full_data:
                         full_data["adc_vl_f"] * full_data["adc_il_f"]),
            },
        "plot_metadata": {
            "plot_title": "Load Power",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "blue",
            "increasing_color": "orange",
            "dtick": 5,
            "range": [0, 30],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0.00, 1.00], "red"),
                ([1.00, 8.00], "orange"),
                ([8.00, 12.0], "yellow"),
                ([12.0, 16.0], "green"),
                ([16.0, 19.0], "blue"),
                ([19.0, 20.0], "yellow"),
                ([20.0, 25.0], "orange"),
                ([25.0, 99.9], "red"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " W",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "batterytemp": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": "t_batt",
            },
        "plot_metadata": {
            "plot_title": "Battery Temperature",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "blue",
            "increasing_color": "orange",
            "dtick": 20,
            "range": [-20, 80],
            "tick0": -10,
            "steps": sindri.templates.generate_step_string((
                ([-20, -10], "navy"),
                ([-10, 0.0], "blue"),
                ([0.0, 10.], "teal"),
                ([10., 50.], "green"),
                ([50., 60.], "yellow"),
                ([60., 70.], "orange"),
                ([70., 200], "red"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "°C",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "triggerrate": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": (
                lambda full_data:
                round(-1 * full_data["bytes_remaining"].diff(5)
                      / (TRIGGER_SIZE_MB * 1e6)).clip(lower=0)
                / round((full_data["time"].diff(5)).dt.total_seconds() / 60)),
            },
        "plot_metadata": {
            "plot_title": "Trigger Rate",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "blue",
            "increasing_color": "orange",
            "dtick": 10,
            "range": [0, 60],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0., 1.], "navy"),
                ([1., 5.], "blue"),
                ([5., 10], "teal"),
                ([10, 20], "green"),
                ([20, 30], "lime"),
                ([30, 40], "yellow"),
                ([40, 50], "orange"),
                ([50, 99], "red"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "/min",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "triggersremaining": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": (
                lambda full_data:
                full_data["bytes_remaining"] / (1e6 * TRIGGER_SIZE_MB)),
            },
        "plot_metadata": {
            "plot_title": "Triggers Remaining",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 3600,
            "range": [0, 21600],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0.000, 60.00], "red"),
                ([60.00, 1800.], "orange"),
                ([1800., 3600.], "yellow"),
                ([3600., 7200.], "lime"),
                ([7200., 99999], "green"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "crcerrors": {
        "plot_type": "custom",
        "plot_data": {
            "data_functions": (
                lambda full_data, data_args:
                full_data["crc_errors"].diff(1).clip(lower=0).last("1D").sum(),
                lambda full_data, data_args:
                full_data["crc_errors"].diff(1).clip(lower=0).last("1H").sum(),
                lambda full_data, data_args:
                full_data["crc_errors"].last("24H").max(),
                ),
            },
        "plot_metadata": {
            "plot_title": "CRC Errors",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 20,
            "range": [0, 100],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0.00, 0.90], "green"),
                ([0.90, 5.00], "lime"),
                ([5.00, 12.5], "yellow"),
                ([12.5, 25.0], "orange"),
                ([25.0, 50.0], "red"),
                ([50.0, 9999], "maroon"),
                )),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "",
            "plot_update_code": sindri.templates.GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    }


def safe_nan(value):
    if math.isnan(value) or np.isnan(value):
        return SENTINEL_VALUE_JSON
    return value


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if math.isnan(obj) or np.isnan(obj):
                return SENTINEL_VALUE_JSON
        except Exception:
            pass
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, (np.bool, np.bool_)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.to_list()
        return json.JSONEncoder.default(self, obj)


def get_plot_data(plot_type=None, **kwargs):
    if not plot_type:
        return None

    data_args = copy.deepcopy(STATUS_DATA_ARGS_DEFAULT)
    data_args.update(**kwargs)
    full_data = sindri.plot.load_status_data(latest_n=3)

    plot_data = []
    if plot_type == "numeric":
        if callable(data_args["variable"]):
            base_data = data_args["variable"](full_data)
        else:
            base_data = full_data.loc[:, data_args["variable"]]

        if data_args["threshold_type"]:
            if data_args["threshold_type"] == "min":
                data_args["overlay_functions"][2] = lambda val: min(val)
            elif data_args["threshold_type"] == "max":
                data_args["overlay_functions"][2] = lambda val: max(val)
            elif data_args["threshold_type"] == "mean":
                data_args["overlay_functions"][2] = (
                    lambda val: sum(val) / len(val))
            else:
                raise ValueError(
                    "Either overlay_functions must be defined or "
                    "threshold_type must be one of {'min', 'max', 'mean'} "
                    "with plot_type 'numeric', not "
                    + str(data_args['threshold_type'])
                    )

    elif plot_type == "custom":
        base_data = full_data
    else:
        raise ValueError("Plot type must be one of {None, 'numeric'}, not "
                         + str(plot_type))

    plot_data = tuple(safe_nan(overlay_function(data_function(base_data,
                                                              data_args)))
                      for data_function, overlay_function
                      in zip(data_args["data_functions"],
                             data_args["overlay_functions"]))

    return plot_data


def generate_status_data(status_dashboard_plots=STATUS_DASHBOARD_PLOTS,
                         write_dir=None, write_path=STATUS_JSON_PATH):
    status_data = {}
    status_data["lastupdatetimestamp"] = int(time.time() * 1000)
    for plot_id, plot in status_dashboard_plots.items():
        if plot["plot_type"]:
            try:
                plot_data = get_plot_data(
                    plot_type=plot["plot_type"], **plot["plot_data"])
            except Exception:
                plot_data = [SENTINEL_VALUE_JSON for __ in range(3)]
            status_data[plot_id] = plot_data

    if write_dir is not None and write_dir is not False and status_data:
        with open(Path(write_dir) / write_path, "w",
                  encoding="utf-8", newline="\n") as jsonfile:
            json.dump(status_data, jsonfile,
                      separators=(",", ":"), cls=CustomJSONEncoder)
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
        sentinel_value_json=SENTINEL_VALUE_JSON,
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
