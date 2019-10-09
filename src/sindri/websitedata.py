"""
Data, plots and calculations for the HAMMA Mjolnir status website.
"""

# Standard library imports
import json
from pathlib import Path

# Local imports
import sindri.templates
from sindri.utils import WEBSITE_UPDATE_FREQUENCY_MIN as UPDATE_FREQ


STATUS_JSON_PATH = Path("status_data.json")


STATUS_DASHBOARD_PLOTS = (
    {
        "plot_id": "weblatency",
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
            "range": [0, UPDATE_FREQ * 2.5],
            "tick0": 0,
            "steps": sindri.templates.generate_step_string((
                ([0, UPDATE_FREQ], "green"),
                ([UPDATE_FREQ, UPDATE_FREQ + 1], "yellow"),
                ([UPDATE_FREQ + 1, UPDATE_FREQ + 3], "orange"),
                ([UPDATE_FREQ + 3, UPDATE_FREQ * 2.5], "red"),
                )),
            "threashold_value": UPDATE_FREQ,
            "number_suffix": " min",
            "plot_update_code": (
                "plot.data[0].value = (new Date() "
                "- new Date(document.lastModified)) / (1000 * 60);\n"
                f"plot.data[0].delta.reference = {UPDATE_FREQ};\n"
                ),
            },
        },
    {
        "plot_id": "battvoltage",
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
                ([10.0, 10.4], "red"),
                ([10.4, 11.0], "orange"),
                ([11.0, 12.0], "yellow"),
                ([12.0, 14.2], "green"),
                ([14.2, 14.6], "yellow"),
                ([14.6, 14.9], "orange"),
                ([14.9, 15.0], "red"),
                )),
            "threashold_value": 13.1,
            "number_suffix": " V",
            "plot_update_code": (
                "plot.data[0].value = statusData.battvoltage[0];\n"
                "plot.data[0].delta.reference = statusData.battvoltage[1];\n"
                ),
            },
        },
    )


def generate_status_data(write_dir=None, write_path=STATUS_JSON_PATH):
    full_data = sindri.plot.load_status_data(latest_n=2)
    status_data = {
        "battvoltage": [
            full_data.loc[:, "adc_vb_f"].iloc[-1],
            full_data.loc[:, "adc_vb_f"].iloc[-60],
            ],
        }
    if write_dir is not None and write_dir is not False:
        with open(Path(write_dir) / write_path, "w",
                  encoding="utf-8", newline="\n") as jsonfile:
            json.dump(status_data, jsonfile, separators=(",", ":"))
    return status_data


def generate_dashboard_block(status_dashboard_plots=STATUS_DASHBOARD_PLOTS):
    widget_blocks = []
    plot_array = []
    for plot in status_dashboard_plots:
        widget_block = sindri.templates.DASHBOARD_ITEM_TEMPLATE.format(
            plot_id=plot["plot_id"], **plot["plot_metadata"])
        widget_blocks.append(widget_block)
        plot_setup = sindri.templates.DASHBOARD_PLOT_TEMPLATE.format(
            plot_id=plot["plot_id"], **plot["plot_params"])
        plot_array.append(plot_setup)
    widgets = "\n".join(widget_blocks)
    update_script = sindri.templates.DASHBOARD_SCRIPT_TEMPLATE.format(
        plot_array="\n".join(plot_array), status_json_path=STATUS_JSON_PATH)
    dashboard_section = sindri.templates.DASHBOARD_SECTION_TEMPLATE.format(
        widgets=widgets, update_script=update_script)
    return dashboard_section


def generate_mainfile_content():
    mainfile_content = sindri.templates.MAINPAGE_SENSOR_TEMPLATE.format(
        main_content="\n".join((
            generate_dashboard_block(),
            )))
    return mainfile_content
