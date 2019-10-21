"""
Data, plots and calculations for the HAMMA Mjolnir status website.
"""

# Standard library imports
import copy
import datetime
import json
import math
import os
from pathlib import Path
import shutil
import time

# Third party imports
import numpy as np
import pandas as pd

# Local imports
import sindri.process
import sindri.utils.misc
import sindri.website.templates


CONTENT_PATH = Path("content")
ASSET_PATH = Path("assets")
THEME_PATH = Path("themes")
DATABAG_PATH = Path("databags")

MAINPAGE_PATH = CONTENT_PATH / "contents.lr"
BUILDINFO_DATABAG_PATH = DATABAG_PATH / "buildinfo.json"
LEKTOR_ICON_VERSION_PATH = THEME_PATH / "lektor-icon" / "_version.txt"

LASTUPDATE_FILENAME = "{section_id}_lastupdate.json"
DATA_FILENAME = "{section_id}_data.json"
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


def generate_dashboard_data(full_data, dashboard_plots, output_path=None):
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


def generate_table_data(full_data, output_cols,
                        time_period=None, drop_cols=None, col_conversions=None,
                        sort_rows=False, reset_index=True, final_colnames=None,
                        output_args=None, output_path=None):
    if time_period:
        full_data = full_data.last(time_period)
    full_data = full_data.copy()
    if drop_cols:
        full_data = full_data.drop(list(drop_cols), axis=1)

    if col_conversions:
        for var_name, (factor, n_digits) in col_conversions.items():
            full_data[var_name] = round(full_data[var_name] * factor, n_digits)

    table_data = pd.concat(tuple(col_fn(full_data) for col_fn in output_cols),
                           axis=1, sort=sort_rows)

    if reset_index:
        table_data.reset_index(inplace=True)
    if final_colnames:
        table_data.columns = list(final_colnames)

    if output_path:
        if output_args is None:
            output_args = {}
        table_data.to_json(
            output_path, orient="records", lines=False, **output_args)
    return table_data


def generate_text_data(
        input_path, output_path=None, output_path_full=None, n_lines=None):
    if output_path is None:
        output_path = output_path_full

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
    if project_path:
        project_path = Path(project_path) / ASSET_PATH
    else:
        project_path = Path()

    full_data = sindri.process.ingest_status_data(n_days=31)
    data_input_path = sindri.process.get_status_data_paths(n_days=-1)[-1]

    for block_type, block_metadata, block_args in mainpage_blocks:
        input_path = Path(block_args["data_args"]
                          .get("input_path", data_input_path)).expanduser()
        update_needed = check_update(
            input_path,
            project_path / (LASTUPDATE_FILENAME.format(
                section_id=block_metadata["section_id"])),
            )
        if not update_needed:
            continue

        data_args = copy.deepcopy(block_args["data_args"])
        if data_args.get("input_path", None) is not None:
            data_args["input_path"] = input_path
        if data_args.get("output_path", None) is None:
            data_args["output_path"] = DATA_FILENAME.format(
                section_id=block_metadata["section_id"])
        for data_arg in ("output_path", "output_path_full"):
            if data_args.get(data_arg, None) is not None:
                data_args[data_arg] = project_path / data_args[data_arg]

        if block_type == "dashboard":
            generate_dashboard_data(full_data=full_data.last("27H"),
                                    **data_args)
        if block_type == "table":
            generate_table_data(full_data=full_data, **data_args)
        if block_type == "text":
            generate_text_data(**data_args)


def generate_step_string(color_domain, color_range):
    if len(color_domain) != (len(color_range) - 1):
        raise ValueError("Color domain and range lengths do not align "
                         f"(are {len(color_domain)} and {len(color_range)}).")
    color_domain = [-1e9] + color_domain + [1e9]
    step_string = "".join((
        sindri.website.templates.GAUGE_PLOT_STEPS_TEMPLATE.format(
            begin=begin, end=end, color=color)
        for begin, end, color in
        zip(color_domain[:-1], color_domain[1:], color_range)))
    return step_string


def generate_steps(plot, color_map=None):
    steps = plot["plot_params"].get("steps", None)
    if steps is False:
        return ""
    if steps is None:
        if color_map is None:
            return ""
        plot_variable = plot["plot_data"].get("variable", None)
        if plot_variable is None:
            return ""
        steps = color_map.get(plot_variable, None)
        if steps is None:
            return ""
    return generate_step_string(*steps)


def generate_dashboard_block(
        block_metadata,
        data_args,
        color_map=None,
        update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS,
        update_interval_fast_seconds=STATUS_UPDATE_INTERVAL_FAST_SECONDS,
        ):
    widget_blocks = []
    all_plots = []
    fast_update_plots = []
    for plot_id, plot in data_args["dashboard_plots"].items():
        plot["plot_params"]["steps"] = generate_steps(plot, color_map)
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


def generate_table_block(
        block_metadata, data_args, color_map,
        update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS):
    table_content = sindri.website.templates.TABLE_CONTENT_TEMPLATE.format(
        section_id=block_metadata["section_id"],
        color_map=color_map,
        final_colnames=list(data_args["final_colnames"]),
        data_path=DATA_FILENAME.format(
            section_id=block_metadata["section_id"]),
        lastupdate_path=LASTUPDATE_FILENAME.format(
            section_id=block_metadata["section_id"]),
        update_interval_seconds=update_interval_seconds,
        )
    table_block = sindri.website.templates.CONTENT_SECTION_TEMPLATE.format(
        content=table_content, full_width="true", **block_metadata)
    return table_block


def generate_text_block(
        block_metadata,
        data_args,
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
        content=text_content, button_link=text_path_full, full_width="true",
        **block_metadata)
    return text_block


def generate_mainfile_content(mainpage_blocks):
    rendered_blocks = []
    for block_type, block_metadata, block_args in mainpage_blocks:
        if block_type == "dashboard":
            rendered_block = generate_dashboard_block(
                block_metadata=block_metadata, **block_args)
        elif block_type == "table":
            rendered_block = generate_table_block(block_metadata, **block_args)
        elif block_type == "text":
            rendered_block = generate_text_block(block_metadata, **block_args)
        else:
            raise ValueError("Block type must be one of "
                             "{'dashboard', 'table', 'text'}")
        rendered_blocks.append(rendered_block)
    mainfile_content = (sindri.website.templates.MAINPAGE_SENSOR_TEMPLATE
                        .format(main_content="\n".join(rendered_blocks)))
    return mainfile_content


def generate_build_info(project_path=None):
    if project_path is None:
        project_path = Path()

    build_time = datetime.datetime.utcnow()
    sindri_version = sindri.__version__

    lektor_version = "NULL"
    imported_pkg_resources = False
    try:
        import pkg_resources
        imported_pkg_resources = True
    except Exception:
        try:
            import pip._vendor.pkg_resources as pkg_resources
            imported_pkg_resources = True
        except Exception as e:
            print("Error importing pkg_resources to get version string: "
                  f"{type(e)} : {e}")

    try:
        for package in pkg_resources.working_set:
            if package.project_name.lower() == "lektor":
                lektor_version = package.version
                break
    except Exception as e:
        if imported_pkg_resources:
            print("Error getting Lektor version from pkg_resources: "
                  f"{type(e)} : {e}")

    try:
        with open(Path(project_path) / LEKTOR_ICON_VERSION_PATH, "r",
                  encoding="utf-8") as lektor_icon_version_file:
            lektor_icon_version = lektor_icon_version_file.read()
    except Exception as e:
        print("Error getting Lektor-Icon version string: "
              f"{type(e)} : {e}")
        lektor_icon_version = "NULL"

    version_string_template = (
        "<a href='{pkg_link}' target='_blank' rel='noopener noreferrer'>"
        "{pkg_name}</a>&nbsp;{pkg_version}"
        )

    time_string = f"Site Build Timestamp: {build_time} UTC"
    version_strings = tuple(
        version_string_template.format(
            pkg_name=pkg_name.replace("-", "&#8209;"),
            pkg_version=pkg_version, pkg_link=pkg_link)
        for pkg_name, pkg_version, pkg_link in (
            ("Sindri", sindri_version, "https://github.com/hamma-dev/sindri"),
            ("Lektor", lektor_version, "https://www.getlektor.com/"),
            ("Lektor-Icon", lektor_icon_version,
             "https://spyder-ide.github.io/lektor-icon/"),
            ))

    version_string_combined = " <span class='pipe-colored'>|</span> ".join(
        version_strings)
    build_info_string = "<br>".join((version_string_combined, time_string))
    build_info = {"buildinfo": build_info_string}

    return build_info


def generate_content(mainpage_blocks, project_path=None):
    if project_path is None:
        project_path = Path()
    else:
        project_path = Path(project_path)

    build_info = generate_build_info(project_path=project_path)
    os.makedirs((project_path / BUILDINFO_DATABAG_PATH).parent, exist_ok=True)
    write_data_json(build_info, project_path / BUILDINFO_DATABAG_PATH)

    mainfile_content = generate_mainfile_content(mainpage_blocks)
    with open(project_path / MAINPAGE_PATH, "w",
              encoding="utf-8", newline="\n") as main_file:
        main_file.write(mainfile_content)
