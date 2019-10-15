"""
Data, plots and calculations for the HAMMA Mjolnir status website.
"""

# Standard library imports
import copy
import json
import math
from pathlib import Path
import shutil
import time

# Third party imports
import numpy as np

# Local imports
import sindri.process
import sindri.utils.misc
import sindri.website.templates


CONTENT_PATH = Path("content")
ASSET_PATH = Path("assets")
MAINPAGE_PATH = Path("content") / "contents.lr"
LASTUPDATE_FILENAME = "{section_id}_lastupdate"
DATA_FILENAME = "{section_id}_data"
LOGFILE_NAME = "brokkr.log"

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
    with open(path, "w", encoding="utf-8", newline="\n") as jsonfile:
        json.dump(output_data, jsonfile,
                  separators=(",", ":"), cls=CustomJSONEncoder)


def write_lastupdate_json(path=None, lastupdate=None,
                          lastupdate_data=None, extra_data=None):
    if extra_data:
        output_data = extra_data
    else:
        output_data = {}

    output_data["lastCheck"] = int(time.time() * 1000)
    if lastupdate is None:
        output_data["lastUpdate"] = int(time.time() * 1000)
    else:
        output_data["lastUpdate"] = lastupdate
    if lastupdate_data is not None:
        output_data["lastUpdateData"] = int(lastupdate_data)

    if path:
        write_data_json(output_data=output_data, path=path)
    return output_data


def check_update(input_path, lastupdate_path):
    current_lastupdate = Path(input_path).stat().st_mtime_ns // 1000000
    if Path(lastupdate_path).exists():
        with open(lastupdate_path, "r",
                  encoding="utf-8", newline="\n") as oldfile:
            old_lastupdate = json.load(oldfile)
        if old_lastupdate["lastUpdateData"] == current_lastupdate:
            write_lastupdate_json(
                lastupdate_path, lastupdate=old_lastupdate["lastUpdate"],
                lastupdate_data=current_lastupdate)
            return False
    write_lastupdate_json(path=lastupdate_path,
                          lastupdate_data=current_lastupdate)
    return True


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
        full_data, dashboard_plots, input_path=None,
        output_path=None, lastupdate_path=None, project_path=None):
    if project_path:
        project_path = Path(project_path) / ASSET_PATH
    else:
        project_path = Path(".")
    if output_path is not None:
        output_path = project_path / output_path
    if lastupdate_path is not None:
        lastupdate_path = project_path / lastupdate_path

    if lastupdate_path is not None:
        update_needed = check_update(input_path, lastupdate_path)
        if not update_needed:
            return None

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


def generate_text_data(input_path, output_path=None, lastupdate_path=None,
                       output_path_full=None, n_lines=None, project_path=None):
    input_path = Path(input_path).expanduser()
    if project_path:
        project_path = Path(project_path) / ASSET_PATH
    else:
        project_path = Path(".")
    if output_path is not None:
        output_path = project_path / output_path
    if output_path_full is not None:
        output_path_full = project_path / output_path_full
    if lastupdate_path is not None:
        lastupdate_path = project_path / lastupdate_path
    if output_path is None:
        output_path = output_path_full

    if lastupdate_path is not None:
        update_needed = check_update(input_path, lastupdate_path)
        if not update_needed:
            return None

    if n_lines is None and output_path_full is None:
        output_path_full = output_path
    if output_path_full is not None:
        shutil.copy(input_path, output_path_full)

    if output_path is None or output_path != output_path_full:
        with open(input_path, "r", encoding="utf8", newline="\n") as in_file:
            text_content = in_file.read()
        if n_lines is not None:
            text_content = "\n".join(
                text_content.split("\n")[(-1 * n_lines - 1):-1]) + "\n"
        if output_path:
            with open(output_path, "w",
                      encoding="utf8", newline="\n") as out_file:
                out_file.write(text_content)
        return text_content

    return None


def generate_data(mainpage_blocks, project_path=None):
    if project_path is None:
        project_path = Path()

    full_data = sindri.process.ingest_status_data(n_days=31)
    data_input_path = sindri.process.get_status_data_paths(n_days=-1)[-1]

    for block_type, block_metadata, block_args in mainpage_blocks:
        if block_type == "dashboard":
            generate_dashboard_data(
                full_data=full_data.last("27H"),
                dashboard_plots=block_args["dashboard_plots"],
                input_path=data_input_path,
                output_path=DATA_FILENAME.format(
                    section_id=block_metadata["section_id"]) + ".json",
                lastupdate_path=LASTUPDATE_FILENAME.format(
                    section_id=block_metadata["section_id"]) + ".json",
                project_path=project_path,
                )
        if block_type == "text":
            generate_text_data(
                lastupdate_path=LASTUPDATE_FILENAME.format(
                    section_id=block_metadata["section_id"]) + ".json",
                project_path=project_path,
                **block_args["data_args"],
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
        section_id=block_metadata["section_id"],
        all_plots="\n".join(all_plots),
        data_path=DATA_FILENAME.format(
            section_id=block_metadata["section_id"]),
        lastupdate_path=LASTUPDATE_FILENAME.format(
            section_id=block_metadata["section_id"]),
        update_interval_seconds=update_interval_seconds,
        fast_update_plots=fast_update_plots,
        update_interval_fast_seconds=update_interval_fast_seconds,
        )
    dashboard_block = (sindri.website.templates.DASHBOARD_SECTION_TEMPLATE
                       .format(widgets=widgets, update_script=update_script,
                               **block_metadata))
    return dashboard_block


def generate_text_block(block_metadata, data_args,
                        replace_items="[]",
                        update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS,
                        ):
    if data_args["output_path_full"] is None:
        text_path_full = data_args["output_path"]
    else:
        text_path_full = data_args["output_path_full"]
    if data_args["output_path"] is None:
        text_path = data_args["output_path_full"]
    else:
        text_path = data_args["output_path"]

    text_content = sindri.website.templates.TEXT_CONTENT_TEMPLATE.format(
        section_id=block_metadata["section_id"],
        replace_items=replace_items,
        text_path=text_path,
        lastupdate_path=LASTUPDATE_FILENAME.format(
            section_id=block_metadata["section_id"]),
        update_interval_seconds=update_interval_seconds,
        )
    text_block = sindri.website.templates.CONTENT_SECTION_TEMPLATE.format(
        content=text_content, button_link=text_path_full, **block_metadata)
    return text_block


def generate_mainfile_content(mainpage_blocks):
    rendered_blocks = []
    for block_type, block_metadata, block_args in mainpage_blocks:
        if block_type == "dashboard":
            rendered_block = generate_dashboard_block(
                block_metadata=block_metadata, **block_args)
        elif block_type == "text":
            rendered_block = generate_text_block(block_metadata, **block_args)
        else:
            raise ValueError("Block type must be one of {'dashboard', 'text'}")
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
