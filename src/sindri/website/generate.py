"""
Data, plots and calculations for the HAMMA Mjolnir status website.
"""

# Standard library imports
import copy
import datetime
import json
import os
from pathlib import Path
import shutil
import time

# Third party imports
import numpy as np
import pandas as pd

# Local imports
import sindri.process
import sindri.website.templates


CONTENT_PATH = Path("content")
ASSET_PATH = Path("assets")
THEME_PATH = Path("themes")
DATABAG_PATH = Path("databags")
CONTENT_FILENAME = "contents.lr"

BUILDINFO_DATABAG_PATH = DATABAG_PATH / "buildinfo.json"
LEKTOR_ICON_VERSION_PATH = THEME_PATH / "lektor-icon" / "_version.txt"

LASTUPDATE_FILENAME = "{section_id}_lastupdate.json"
DATA_FILENAME = "{section_id}_data.{extension}"
DEFAULT_EXTENSION = "json"

STATUS_UPDATE_INTERVAL_SECONDS = 10
STATUS_UPDATE_INTERVAL_FAST_SECONDS = 1
STATUS_UPDATE_INTERVAL_SLOW_SECONDS = 300


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
    if not np.isfinite(value):
        return None
    return value


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if not np.isfinite(obj):
                return None
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


def write_data_json(output_data, path, by_line=False):
    if by_line:
        separators = (",\n", ":")
    else:
        separators = (",", ":")
    with open(path, "w", encoding="utf-8", newline="\n") as jsonfile:
        json.dump(output_data, jsonfile,
                  separators=separators, cls=CustomJSONEncoder)


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


def process_tabular_data(
        full_data,
        time_period=None, drop_cols=None, decimate=None,
        col_conversions=None, preprocess_fn=None,
        output_cols=None, sort_rows=False,
        round_floats=None, reset_index=False, index_postprocess=False,
        final_colnames=None, reverse_output=False
        ):
    if time_period:
        full_data = full_data.last(time_period)
    full_data = full_data.copy()
    if decimate and decimate > 1:
        full_data = full_data.iloc[::decimate, :]
    if drop_cols:
        full_data = full_data.drop(list(drop_cols), axis=1, errors="ignore")

    if col_conversions:
        for var_name, (factor, n_digits) in col_conversions.items():
            full_data[var_name] = round(full_data[var_name] * factor, n_digits)

    if preprocess_fn:
        full_data = preprocess_fn(full_data)

    if output_cols is None:
        output_data = full_data
    elif callable(output_cols[0]):
        output_data = pd.concat((col_fn(full_data) for col_fn in output_cols),
                                axis=1, sort=sort_rows)
    else:
        output_data = full_data[[col for col in output_cols]]

    if round_floats:
        output_data = round(output_data, round_floats)
    index_name = output_data.index.name if output_data.index.name else "index"
    if reset_index:
        output_data.reset_index(inplace=True)
    if index_postprocess:
        if reset_index:
            output_data[index_name] = index_postprocess(
                output_data[index_name])
        else:
            output_data.index = index_postprocess(output_data.index)
    if final_colnames:
        output_data.columns = list(final_colnames)
    if reverse_output:
        output_data = output_data.iloc[::-1, :]

    return output_data


def get_dashboard_plot_data(full_data, plot_type, **kwargs):
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
        full_data, dashboard_plots,
        output_path=None,
        ):
    dashboard_data = {}
    for plot_id, plot in dashboard_plots.items():
        if plot["plot_type"]:
            try:
                plot_data = get_dashboard_plot_data(
                    full_data,
                    plot_type=plot["plot_type"],
                    **plot["plot_data"],
                    )
            except Exception as e:
                print(str(type(e)), e)
                plot_data = [None for __ in range(3)]
            dashboard_data[plot_id] = plot_data

    if dashboard_data and output_path:
        write_data_json(output_data=dashboard_data, path=output_path)
    return dashboard_data


def generate_table_data(
        full_data, output_cols=None, output_args=None, output_path=None,
        **table_process_args):

    table_data = process_tabular_data(
        full_data=full_data, output_cols=output_cols, **table_process_args)

    if output_path:
        if output_args is None:
            output_args = {}
        table_data.to_json(
            output_path, orient="records", lines=False, **output_args)
    return table_data


def generate_text_data(
        input_path,
        full_data=None, output_path=None, output_path_full=None, n_lines=None,
        ):
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


def generate_plot_data(
        full_data, plot_subplots=None, index_converter=None, output_path=None,
        **table_process_args):

    plot_data = process_tabular_data(
        full_data=full_data, output_cols=list(plot_subplots.keys()),
        **table_process_args)

    if output_path:
        plot_data_json = (
            plot_data.where(np.isfinite(plot_data), None)
            .to_dict(orient="list"))
        if plot_data.index.name:
            index_name = plot_data.index.name
        else:
            index_name = "index"
        if index_converter is None:
            plot_data_json[index_name] = list(plot_data.index)
        else:
            plot_data_json[index_name] = list(index_converter(plot_data.index))
        write_data_json(plot_data_json, output_path, by_line=True)
    return plot_data


def generate_singlepage_data(page_blocks, full_data,
                             input_path_default=None, output_path=None):
    data_function_map = {
        "dashboard": generate_dashboard_data,
        "table": generate_table_data,
        "text": generate_text_data,
        "plot": generate_plot_data,
        }

    for section_id, block in page_blocks.items():
        if block["type"] == "generic":
            continue
        input_path = Path(block["args"]["data_args"]
                          .get("input_path", input_path_default))

        # Handle input path if it is a glob
        if "*" in input_path.stem or "?" in input_path.stem:
            input_path = Path(input_path).expanduser()
            input_path = Path(list(
                input_path.parents[0].glob(input_path.stem))[0])
            block["args"]["data_args"]["input_path"] = Path(input_path)

        if input_path is not None and output_path is not None:
            input_path = input_path.expanduser()
            update_needed = check_update(
                input_path,
                output_path / (LASTUPDATE_FILENAME.format(
                    section_id=section_id)),
                )
            if not update_needed:
                continue

        data_args = copy.deepcopy(block["args"]["data_args"])
        if data_args.get("input_path", None) is not None:
            data_args["input_path"] = input_path
        if data_args.get("output_path", None) is None:
            data_args["output_path"] = DATA_FILENAME.format(
                section_id=section_id, extension=DEFAULT_EXTENSION)
        for data_arg in ("output_path", "output_path_full"):
            if data_args.get(data_arg, None) is not None:
                data_args[data_arg] = output_path / data_args[data_arg]

        data_function_map[block["type"]](full_data=full_data, **data_args)


def generate_daily_data(
        page_blocks, full_data, input_path_default, output_path,
        filename_template, file_grouper,
        output_args=None, **table_process_args):
    if output_args is None:
        output_args = {}

    for section_id in page_blocks:
        if page_blocks[section_id]["type"] == "generic":
            continue
        update_needed = check_update(
            input_path_default,
            output_path / (LASTUPDATE_FILENAME.format(section_id=section_id)))
        if not update_needed:
            continue
    if not update_needed:
        return

    output_data = process_tabular_data(full_data, **table_process_args)

    output_data_grouped = output_data.groupby(file_grouper, sort=False)
    for group in output_data_grouped.groups:
        try:
            group_data = output_data_grouped.get_group(group)
        # Skip if no data for this day
        except KeyError:
            continue
        filename = filename_template.format(group.date())
        group_data.to_csv(output_path / filename, line_terminator="\n",
                          **output_args)


def generate_site_data(content_pages, project_path=None):
    full_data = sindri.process.ingest_status_data(n_days=30)
    input_path_default = sindri.process.get_status_data_paths(n_days=1)[0]
    if project_path:
        project_path = Path(project_path) / ASSET_PATH
    else:
        project_path = Path()

    for path, page in content_pages.items():
        output_path = project_path / path
        os.makedirs(output_path, exist_ok=True)
        if page["type"] is None:
            continue
        common_args = {
            "page_blocks": page["blocks"],
            "full_data": full_data,
            "input_path_default": input_path_default,
            "output_path": output_path,
            }
        if page["type"] == "singlepage":
            generate_singlepage_data(**common_args)
        elif page["type"] == "daily":
            generate_daily_data(**common_args, **page["args"])
        else:
            raise ValueError(
                "Page type must be one of {None, 'singlepage', 'daily'}, "
                f"not {page['type']} for page at path {path}")


def lookup_in_map(param, param_map):
    if param_map is None or param is None:
        return {}
    map_result = param_map.get(param, None)
    if map_result is None:
        return {}
    return copy.deepcopy(map_result)


def generate_step_strings(color_domain, color_range, endpoints,
                          template_string, **extra_args):
    if len(color_domain) != (len(color_range) - 1):
        raise ValueError("Color domain and range lengths do not align "
                         f"(are {len(color_domain)} and {len(color_range)}).")
    color_domain = (list(endpoints[:1])
                    + list(color_domain)
                    + list(endpoints[-1:]))
    step_strings = tuple(
        template_string.format(begin=begin, end=end, color=color, **extra_args)
        for begin, end, color in
        zip(color_domain[:-1], color_domain[1:], color_range))
    return step_strings


def generate_steps(plot, color_map=None):
    steps = plot["plot_params"].get("steps", None)
    if steps is False:
        return ""
    if steps is None:
        steps = lookup_in_map(plot["plot_data"].get("variable", None),
                              color_map)
    if not steps:
        return ""
    step_strings = generate_step_strings(
        *steps, endpoints=[-1e9, 1e9],
        template_string=sindri.website.templates.GAUGE_PLOT_STEPS_TEMPLATE)
    return " ".join(step_strings)


def generate_generic_block(
        block_metadata, section_id, content,
        data_args=None, data_path=None, lastupdate_path=None):
    generic_block = sindri.website.templates.CONTENT_SECTION_TEMPLATE.format(
        content=content,
        full_width="true",
        section_id=section_id,
        **block_metadata,
        )
    return generic_block


def generate_dynamic_block(
        default_query_params, button_left_text, button_right_text,
        section_id, **generic_args):
    query_param_parser = sindri.website.templates.QUERY_PARAM_PARSER.format(
        default_query_params=default_query_params)
    content_block = sindri.website.templates.DYNAMIC_PAGE_TOP_SECTION.format(
        section_id=section_id,
        query_param_parser=query_param_parser,
        button_left_text=button_left_text,
        button_right_text=button_right_text,
        )
    dynamic_block = generate_generic_block(
        content=content_block, section_id=section_id, **generic_args)
    return dynamic_block


def generate_dashboard_block(
        block_metadata, section_id, data_args,
        data_path, lastupdate_path,
        layout_map=None, color_map=None,
        update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS,
        update_interval_fast_seconds=STATUS_UPDATE_INTERVAL_FAST_SECONDS,
        ):
    widget_blocks = []
    all_plots = []
    fast_update_plots = []
    for plot_id, plot in data_args["dashboard_plots"].items():
        layout_args = lookup_in_map(plot["plot_data"].get("variable", None),
                                    layout_map)
        layout_args["tick0"] = layout_args.get(
            "range", plot["plot_params"].get("range", None))[0]
        plot["plot_params"]["steps"] = generate_steps(plot, color_map)
        widget_block = (sindri.website.templates.DASHBOARD_ITEM_TEMPLATE
                        .format(plot_id=plot_id, **plot["plot_metadata"]))
        widget_blocks.append(widget_block)
        plot_setup = (sindri.website.templates.DASHBOARD_PLOT_TEMPLATE
                      .format(plot_id=plot_id, **plot["plot_params"],
                              **layout_args))
        all_plots.append(plot_setup)
        if plot.get("fast_update", None):
            fast_update_plots.append(plot_id)
    widgets = "\n".join(widget_blocks)
    update_script = sindri.website.templates.DASHBOARD_SCRIPT_TEMPLATE.format(
        section_id=section_id,
        all_plots="\n".join(all_plots),
        data_path=data_path,
        lastupdate_path=lastupdate_path,
        update_interval_seconds=update_interval_seconds,
        fast_update_plots=fast_update_plots,
        update_interval_fast_seconds=update_interval_fast_seconds,
        )
    dashboard_block = (sindri.website.templates.DASHBOARD_SECTION_TEMPLATE
                       .format(widgets=widgets,
                               update_script=update_script,
                               section_id=section_id,
                               **block_metadata,
                               ))
    return dashboard_block


def generate_table_block(
        block_metadata, section_id, data_args,
        data_path, lastupdate_path,
        color_map="{}",
        color_map_axis="column",
        alert_on_fail=False,
        extension=DEFAULT_EXTENSION,
        update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS,
        ):
    final_colnames = data_args.get("final_colnames", None)
    if final_colnames is not None:
        final_colnames = list(final_colnames)
    else:
        final_colnames = []
    data_path = Path(data_path).stem

    table_content = sindri.website.templates.TABLE_CONTENT_TEMPLATE.format(
        section_id=section_id,
        color_map=color_map,
        color_map_axis=color_map_axis,
        final_colnames=final_colnames,
        alert_on_fail=str(alert_on_fail).lower(),
        data_path=data_path,
        extension=extension,
        lastupdate_path=lastupdate_path,
        update_interval_seconds=update_interval_seconds,
        )
    table_block = sindri.website.templates.CONTENT_SECTION_TEMPLATE.format(
        content=table_content,
        full_width="true",
        section_id=section_id,
        **block_metadata,
        )
    return table_block


def generate_text_block(
        block_metadata, section_id, data_args,
        data_path, lastupdate_path,
        replace_items="[]",
        update_interval_seconds=STATUS_UPDATE_INTERVAL_SECONDS,
        ):
    text_content = sindri.website.templates.TEXT_CONTENT_TEMPLATE.format(
        section_id=section_id,
        replace_items=replace_items,
        data_path=data_path,
        lastupdate_path=lastupdate_path,
        update_interval_seconds=update_interval_seconds,
        )
    text_block = sindri.website.templates.CONTENT_SECTION_TEMPLATE.format(
        content=text_content,
        full_width="true",
        section_id=section_id,
        **block_metadata,
        )
    return text_block


def generate_plot_block(
        block_metadata, section_id, data_args, content_args,
        data_path, lastupdate_path,
        name_map=None, layout_map=None, color_map=None,
        extension=DEFAULT_EXTENSION,
        update_interval_seconds=STATUS_UPDATE_INTERVAL_SLOW_SECONDS,
        ):
    idx_strings = []
    subplot_items = []
    yaxis_items = []
    shape_items = []
    data_path = Path(data_path).stem
    content_args["alert_on_fail"] = str(content_args["alert_on_fail"]).lower()

    for idx, subplot_variable in enumerate(data_args["plot_subplots"]):
        idx_string = str(idx + 1) if idx else ""
        idx_strings.append(idx_string)
        layout_args = lookup_in_map(subplot_variable, layout_map)
        layout_args["tick0"] = layout_args["range"][0]
        range_bump = (layout_args["range"][1] - layout_args["range"][0]) * 0.05
        layout_args["range"] = [layout_args["range"][0] - range_bump,
                                layout_args["range"][1] + range_bump]
        subplot_title = lookup_in_map(subplot_variable, name_map)
        if not subplot_title:
            subplot_title = subplot_variable.replace("_", " ").title()

        subplot = sindri.website.templates.SUBPLOT_DATA_TEMPLATE.format(
            subplot_variable=subplot_variable,
            subplot_title=subplot_title,
            idx=idx_string,
            plot_bgcolor=content_args["plot_bgcolor"],
            plot_fgcolor=content_args["plot_fgcolor"],
            )
        subplot_items.append(subplot)

        subplot_yaxis = sindri.website.templates.SUBPLOT_AXIS_TEMPLATE.format(
            subplot_title=subplot_title,
            idx=idx_string,
            plot_fgcolor=content_args["plot_fgcolor"],
            **layout_args,
            )
        yaxis_items.append(subplot_yaxis)

        if color_map and color_map.get(subplot_variable, None):
            shape_strings = generate_step_strings(
                color_map[subplot_variable][0],
                color_map[subplot_variable][1],
                endpoints=layout_args["range"],
                template_string=sindri.website.templates.SHAPE_RANGE_TEMPLATE,
                idx=idx_string,
                shape_opacity=content_args["shape_opacity"],
                )
            shape_items = shape_items + list(shape_strings)

    plot_content = sindri.website.templates.PLOT_CONTENT_TEMPLATE.format(
        section_id=section_id,
        sub_plots="\n".join(subplot_items),
        subplots_list=", ".join(["'[xy{}]'".format(n) for n in idx_strings]),
        y_axes="\n".join(yaxis_items),
        shape_list="\n".join(shape_items),
        data_path=data_path,
        extension=extension,
        lastupdate_path=lastupdate_path,
        update_interval_seconds=update_interval_seconds,
        **content_args,
        )

    plot_block = sindri.website.templates.CONTENT_SECTION_TEMPLATE.format(
        content=plot_content,
        full_width="true",
        section_id=section_id,
        **block_metadata,
        )
    return plot_block


def generate_singlepage_content(page_blocks):
    rendered_blocks = []
    block_function_map = {
        "generic": generate_generic_block,
        "dynamic": generate_dynamic_block,
        "dashboard": generate_dashboard_block,
        "table": generate_table_block,
        "text": generate_text_block,
        "plot": generate_plot_block,
        }

    for section_id, block in page_blocks.items():
        if block["args"]["data_args"].get("output_path", None) is None:
            extension = block["args"].get("extension", DEFAULT_EXTENSION)
            data_path = DATA_FILENAME.format(
                section_id=section_id, extension=extension)
        else:
            data_path = block["args"]["data_args"]["output_path"]
        lastupdate_path = LASTUPDATE_FILENAME.format(section_id=section_id)
        if block["metadata"].get("button_link", None) is True:
            block["metadata"]["button_link"] = data_path
        if block["metadata"].get("button_newtab", None) is not None:
            block["metadata"]["button_newtab"] = str(
                block["metadata"]["button_newtab"]).lower()

        rendered_block = block_function_map[block["type"]](
                block_metadata=block["metadata"],
                section_id=section_id,
                data_path=data_path,
                lastupdate_path=lastupdate_path,
                **block["args"],
                )
        rendered_blocks.append(rendered_block)
    page_content = (sindri.website.templates.SINGLEPAGE_TEMPLATE
                    .format(content_blocks="\n".join(rendered_blocks)))
    return page_content


def generate_build_info(project_path=None, output_path=BUILDINFO_DATABAG_PATH):
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

    if output_path:
        os.makedirs((project_path / output_path).parent, exist_ok=True)
        write_data_json(build_info, project_path / output_path)

    return build_info


def generate_site_content(content_pages, project_path=None):
    if project_path is None:
        project_path = Path()
    else:
        project_path = Path(project_path)

    generate_build_info(project_path=project_path,
                        output_path=project_path / BUILDINFO_DATABAG_PATH)

    page_contents = {}
    for path, page in content_pages.items():
        if page["type"] in {"singlepage", "daily"}:
            page_content = generate_singlepage_content(page["blocks"])
        else:
            raise ValueError(
                f"Page type for {path} must be one of {{'singlepage'}}",
                f"not {page['type']}")
        page_contents[path] = page_content

    return page_contents


def write_site_content(page_contents, project_path=None):
    if project_path is None:
        project_path = Path()
    else:
        project_path = Path(project_path)

    for path, content in page_contents.items():
        content_fullpath = project_path / CONTENT_PATH / path
        os.makedirs(content_fullpath, exist_ok=True)
        with open(content_fullpath / CONTENT_FILENAME, "w",
                  encoding="utf-8", newline="\n") as content_file:
            content_file.write(content)


def generate_and_write_site_content(content_pages, project_path=None):
    page_contents = generate_site_content(
        content_pages, project_path=project_path)
    write_site_content(
        page_contents, project_path=project_path)
    return page_contents
