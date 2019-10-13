"""
Data, plots and calculations for the HAMMA Mjolnir status website.
"""

# Standard library imports
import copy
import json
import math
from pathlib import Path
import time

# Third party imports
import numpy as np

# Local imports
import sindri.process
import sindri.utils.misc
import sindri.website.templates


CONTENT_ROOT_PATH = Path("content")
MAINPAGE_PATH = Path("content") / "contents.lr"
JSON_FILENAME = "{section_id}_data.json"

SENTINEL_VALUE_JSON = -999

STATUS_UPDATE_INTERVAL_SECONDS = 10
STATUS_UPDATE_INTERVAL_FAST_SECONDS = 1


DASHBOARD_DATA_ARGS_DEFAULT = {
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


def write_data_json(output_data, path):
    output_data["lastupdatetimestamp"] = int(time.time() * 1000)
    with open(path, "w", encoding="utf-8", newline="\n") as jsonfile:
        json.dump(output_data, jsonfile,
                  separators=(",", ":"), cls=CustomJSONEncoder)


def get_plot_data(full_data, plot_type, **kwargs):
    if not plot_type:
        return None

    data_args = copy.deepcopy(DASHBOARD_DATA_ARGS_DEFAULT)
    data_args.update(**kwargs)

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


def generate_dashboard_data(
        full_data, dashboard_plots, output_path=None):
    dashboard_data = {}
    for plot_id, plot in dashboard_plots.items():
        if plot["plot_type"]:
            try:
                plot_data = get_plot_data(
                    full_data,
                    plot_type=plot["plot_type"],
                    **plot["plot_data"],
                    )
            except Exception as e:
                print(str(type(e)), e)
                plot_data = [SENTINEL_VALUE_JSON for __ in range(3)]
            dashboard_data[plot_id] = plot_data

    if dashboard_data and output_path:
        write_data_json(output_data=dashboard_data, path=output_path)

    return dashboard_data


def generate_data(mainpage_blocks, project_path=None):
    if project_path is None:
        project_path = Path()

    full_data = sindri.process.ingest_status_data(n=30)

    for block_type, block_metadata, block_args in mainpage_blocks:
        if block_type == "dashboard":
            generate_dashboard_data(
                full_data=full_data.last("26H"),
                dashboard_plots=block_args["dashboard_plots"],
                output_path=(
                    Path(project_path) / CONTENT_ROOT_PATH
                    / JSON_FILENAME.format(
                        section_id=block_metadata["section_id"])),
                )


def generate_dashboard_block(
        block_metadata,
        dashboard_plots,
        update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS,
        update_interval_fast_seconds=STATUS_UPDATE_INTERVAL_FAST_SECONDS,
        ):
    widget_blocks = []
    all_plots = []
    fast_update_plots = []
    for plot_id, plot in dashboard_plots.items():
        widget_block = (sindri.website.templates.DASHBOARD_ITEM_TEMPLATE
                        .format(plot_id=plot_id, **plot["plot_metadata"]))
        widget_blocks.append(widget_block)
        plot_setup = (sindri.website.templates.DASHBOARD_PLOT_TEMPLATE
                      .format(plot_id=plot_id, **plot["plot_params"]))
        all_plots.append(plot_setup)
        if plot.get("fast_update", None):
            fast_update_plots.append(plot_id)
    widgets = "\n".join(widget_blocks)
    update_script = sindri.website.templates.DASHBOARD_SCRIPT_TEMPLATE.format(
        sentinel_value_json=SENTINEL_VALUE_JSON,
        all_plots="\n".join(all_plots),
        data_path=JSON_FILENAME.format(
            section_id=block_metadata["section_id"]),
        update_interval_s=update_interval_seconds,
        fast_update_plots=fast_update_plots,
        update_interval_fast_s=update_interval_fast_seconds,
        )
    dashboard_block = (sindri.website.templates.DASHBOARD_SECTION_TEMPLATE
                       .format(widgets=widgets, update_script=update_script,
                               **block_metadata))
    return dashboard_block


def generate_mainfile_content(mainpage_blocks):
    rendered_blocks = []
    for block_type, block_metadata, block_args in mainpage_blocks:
        if block_type == "dashboard":
            rendered_block = generate_dashboard_block(
                block_metadata=block_metadata, **block_args)
        else:
            raise ValueError("Block type must be one of {'dashboard'}")
        rendered_blocks.append(rendered_block)
    mainfile_content = (sindri.website.templates.MAINPAGE_SENSOR_TEMPLATE
                        .format(main_content="\n".join(rendered_blocks)))
    return mainfile_content


def generate_content(mainpage_blocks, project_path=None):
    if project_path is None:
        project_path = Path()

    mainfile_content = generate_mainfile_content(mainpage_blocks)
    with open(Path(project_path) / MAINPAGE_PATH, "w",
              encoding="utf-8", newline="\n") as main_file:
        main_file.write(mainfile_content)
