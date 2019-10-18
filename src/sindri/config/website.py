"""
Configuration for the plots and tables on the Mjolnir website.
"""

# Standard library imports
import datetime

# Local imports
from sindri.utils.misc import WEBSITE_UPDATE_INTERVAL_S as UPDATE_INT
from sindri.website.templates import (
    GAUGE_PLOT_UPDATE_CODE,
    GAUGE_PLOT_UPDATE_CODE_VALUE,
    GAUGE_PLOT_UPDATE_CODE_COLOR,
)


STATUS_UPDATE_INTERVAL_SECONDS = 10
STATUS_UPDATE_INTERVAL_FAST_SECONDS = 1


STANDARD_COLORS = ["green", "lime", "yellow", "orange", "red"]
STANDARD_COLORS_TEMP = [
    "gray", "blue", "teal", "green", "lime", "yellow", "orange", "red"]


STANDARD_COLOR_TABLES = {
    "notzero": [[-0.5, 0.5], ["red", "green", "red"]],
    "uptime": [[1, 6, 24, 48], STANDARD_COLORS[::-1]],
    "battery_voltage": [[10.4, 11, 11.5, 12, 14, 14.3, 14.6, 15],
                        STANDARD_COLORS[::-1] + STANDARD_COLORS[1:]],
    "array_voltage": [[4, 12, 24, 32], STANDARD_COLORS[::-1]],
    "charge_current": [[0.1, 0.5, 1.0, 2.0], STANDARD_COLORS[::-1]],
    "load_current": [[0.1, 0.5, 0.85, 0.95, 1.65, 1.75, 1.9, 2.0],
                     STANDARD_COLORS[::-1] + STANDARD_COLORS[1:]],
    "temperature": [[-10, 0, 10, 40, 50, 60, 70], STANDARD_COLORS_TEMP],
    "charge_state": [[i + 0.5 for i in range(8)],
                     ["gray", "blue", "maroon", "orange", "red",
                      "yellow", "lime", "green", "teal"]],
    "load_state": [[i + 0.5 for i in range(5)],
                   ["gray", "green", "yellow", "orange", "red", "maroon"]],
    "alarm": [[-0.5, 0.5, 500], ["red", "green", "lime", "red"]],
    "led_state": [[-0.5, 2.5, 6.5, 8.5],
                  ["red", "gray", "green", "yellow", "red"]],
    "power_out": [[0.1, 6, 12, 24], STANDARD_COLORS[::-1]],
    "power_load": [[1, 8, 12, 13.5, 16, 18, 19, 20, 25],
                   STANDARD_COLORS[::-1] + ["teal"] + STANDARD_COLORS[1:]],
    "crc_errors": [[0.98, 5, 12.5, 25], STANDARD_COLORS],
    "crc_errors_delta": [[0.1, 0.9, 1.5, 2.5], STANDARD_COLORS],
    "crc_errors_hourly": [[0.98, 2.5, 5, 10], STANDARD_COLORS],
    "valid_packets": [[0.5, 1.5, 2.5, 4.5], STANDARD_COLORS[::-1]],
    "trigger_rate": [[0.4, 1.4, 3, 6, 15, 30, 49], STANDARD_COLORS_TEMP],
    "triggers_remaining": [[60, 1800, 3500, 7200], STANDARD_COLORS[::-1]],
    "bytes_used": [[0.01, 0.03, 0.05, 0.11], STANDARD_COLORS[::-1]],
    "bytes_remaining": [[n * 0.22 for n in [60, 1800, 3500, 7200]],
                        STANDARD_COLORS[::-1]],
    }


COLOR_TABLE_MAP = {
    "runtime": STANDARD_COLOR_TABLES["uptime"],
    "ping": STANDARD_COLOR_TABLES["notzero"],
    "adc_vb_f": STANDARD_COLOR_TABLES["battery_voltage"],
    "adc_va_f": STANDARD_COLOR_TABLES["array_voltage"],
    "adc_vl_f": STANDARD_COLOR_TABLES["battery_voltage"],
    "adc_ic_f": STANDARD_COLOR_TABLES["charge_current"],
    "adc_il_f": STANDARD_COLOR_TABLES["load_current"],
    "t_hs": STANDARD_COLOR_TABLES["temperature"],
    "t_batt": STANDARD_COLOR_TABLES["temperature"],
    "t_amb": STANDARD_COLOR_TABLES["temperature"],
    "t_rts": STANDARD_COLOR_TABLES["temperature"],
    "charge_state": STANDARD_COLOR_TABLES["charge_state"],
    "array_fault": STANDARD_COLOR_TABLES["notzero"],
    "vb_f": STANDARD_COLOR_TABLES["battery_voltage"],
    "load_state": STANDARD_COLOR_TABLES["load_state"],
    "load_fault": STANDARD_COLOR_TABLES["notzero"],
    "alarm": STANDARD_COLOR_TABLES["alarm"],
    "led_state": STANDARD_COLOR_TABLES["led_state"],
    "power_out": STANDARD_COLOR_TABLES["power_out"],
    "power_load": STANDARD_COLOR_TABLES["power_load"],
    "sweep_vmp": STANDARD_COLOR_TABLES["array_voltage"],
    "sweep_pmax": STANDARD_COLOR_TABLES["power_out"],
    "sweep_voc": STANDARD_COLOR_TABLES["array_voltage"],
    "vb_min_daily": STANDARD_COLOR_TABLES["battery_voltage"],
    "vb_max_daily": STANDARD_COLOR_TABLES["battery_voltage"],
    "array_fault_daily": STANDARD_COLOR_TABLES["notzero"],
    "load_fault_daily": STANDARD_COLOR_TABLES["notzero"],
    "alarm_daily": STANDARD_COLOR_TABLES["alarm"],
    "vb_min": STANDARD_COLOR_TABLES["battery_voltage"],
    "vb_max": STANDARD_COLOR_TABLES["battery_voltage"],
    "sensor_uptime": STANDARD_COLOR_TABLES["uptime"],
    "crc_errors": STANDARD_COLOR_TABLES["crc_errors"],
    "crc_errors_delta": STANDARD_COLOR_TABLES["crc_errors_delta"],
    "crc_errors_hourly": STANDARD_COLOR_TABLES["crc_errors_hourly"],
    "crc_errors_daily": STANDARD_COLOR_TABLES["crc_errors"],
    "valid_packets": STANDARD_COLOR_TABLES["valid_packets"],
    "trigger_rate_1min": STANDARD_COLOR_TABLES["trigger_rate"],
    "trigger_rate_5min": STANDARD_COLOR_TABLES["trigger_rate"],
    "bytes_read": STANDARD_COLOR_TABLES["bytes_used"],
    "bytes_written": STANDARD_COLOR_TABLES["bytes_used"],
    "bytes_remaining": STANDARD_COLOR_TABLES["bytes_remaining"],
    "triggers_remaining": STANDARD_COLOR_TABLES["triggers_remaining"],
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
            "delta_reference": UPDATE_INT,
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": UPDATE_INT / 2,
            "range": [0, UPDATE_INT * 2],
            "tick0": 0,
            "steps": ([UPDATE_INT + ((i + 1) * 60)
                       for i in range(len(STANDARD_COLORS) - 1)],
                      STANDARD_COLORS),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " s",
            "plot_update_code": (
                "data['value'] = (new Date() "
                "- lastCheck_status) / (1000);\n"
                "if (data['value'] > maxLatency_status) {\n"
                "    maxLatency_status = data['value'];\n"
                "    data['gauge.threshold.value'] = data['value'];\n"
                "};\n"
                + GAUGE_PLOT_UPDATE_CODE_COLOR
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
            "steps": ([60, 90, 120, 240], STANDARD_COLORS),
            "threshold_thickness": 0.75,
            "threshold_value": 60,
            "number_color": "white",
            "number_suffix": " s",
            "plot_update_code": (
                "\n".join((
                    *GAUGE_PLOT_UPDATE_CODE_VALUE
                    .splitlines()[0:2],
                    GAUGE_PLOT_UPDATE_CODE_COLOR
                    ))),
            },
        "fast_update": False,
        },
    "sensoruptime": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": "sensor_uptime",
            },
        "plot_metadata": {
            "plot_title": "Sensor Uptime",
            "plot_description": "",
            },
        "plot_params": {
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "dtick": 120,
            "range": [0, 30 * 24],
            "tick0": 0,
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " h",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
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
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " V",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
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
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " V",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
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
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " A",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
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
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "loadpower": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "min",
            "variable": "power_load",
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
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": " W",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
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
            "tick0": -20,
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "°C",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "triggerrate": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": "trigger_rate_5min",
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
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "/min",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "triggersremaining": {
        "plot_type": "numeric",
        "plot_data": {
            "delta_period": "1H",
            "threshold_period": "24H",
            "threshold_type": "max",
            "variable": "triggers_remaining",
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
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    "crcerrors": {
        "plot_type": "custom",
        "plot_data": {
            "data_functions": (
                lambda full_data, data_args:
                full_data.loc[:, "crc_errors_daily"].iloc[-1],
                lambda full_data, data_args:
                full_data.loc[:, "crc_errors_hourly"].iloc[-1],
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
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": 20,
            "range": [0, 100],
            "tick0": 0,
            "steps": STANDARD_COLOR_TABLES["crc_errors"],
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": "white",
            "number_suffix": "",
            "plot_update_code": GAUGE_PLOT_UPDATE_CODE,
            },
        "fast_update": False,
        },
    }


STATUS_DASHBOARD_METADATA = {
    "section_id": "status",
    "section_title": "Status Dashboard",
    "section_description": (
        "Real-time status of this HAMMA sensor and the Mjolnir system."),
    "section_nav_label": "Status",
    }


STATUS_DASHBOARD_DATA_ARGS = {
    "dashboard_plots": STATUS_DASHBOARD_PLOTS,
}


STATUS_DASHBOARD_ARGS = {
    "data_args": STATUS_DASHBOARD_DATA_ARGS,
    "color_map": COLOR_TABLE_MAP,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SECONDS,
    "update_interval_fast_seconds": (
        STATUS_UPDATE_INTERVAL_FAST_SECONDS),
    }


RAW_OUTPUT_METADATA = {
    "section_id": "raw",
    "section_title": "Raw Output Data",
    "section_description": (
        "Raw current and 24-hour max/mean/min Brokkr output data."),
    "section_nav_label": "Data",
    "button_content": "",
    "button_type": "",
    "button_link": "",
    "button_position": "",
    "button_newtab": "",
    }


RAW_OUTPUT_DATA_ARGS = {
    "time_period": "24H",
    "drop_cols": ("time", "timestamp", "sequence_count"),
    "col_conversions": {
        "runtime": (1 / (60 * 60), 2),
        "bytes_read": (1 / 1e9, 2),
        "bytes_written": (1 / 1e9, 2),
        "bytes_remaining": (1 / 1e9, 2),
        },
    "output_cols": (
        lambda full_data: full_data.iloc[-1, :],
        lambda full_data: full_data.min(),
        lambda full_data: full_data.max(),
        lambda full_data: round(full_data.mean(), 2),
        ),
    "sort_rows": False,
    "reset_index": True,
    "final_colnames": ["Variable", "Now", "Min", "Max", "Avg"],
    "output_args": {
        "double_precision": 3, "date_format": "iso", "date_unit": "ms"},
}


RAW_OUTPUT_ARGS = {
    "data_args": RAW_OUTPUT_DATA_ARGS,
    "color_map": COLOR_TABLE_MAP,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SECONDS,
    }


LOG_METADATA = {
    "section_id": "log",
    "section_title": "Client Log",
    "section_description": (
        "Latest log entries from this sensor's Brokkr client."),
    "section_nav_label": "Log",
    "button_content": "View Full Log",
    "button_type": "text",
    "button_position": "bottom",
    "button_newtab": "false",
    }


LOG_DATA_ARGS = {
    "input_path": "~/brokkr.log",
    "output_path": "brokkr_log_latest.txt",
    "output_path_full": "brokkr_log_full.txt",
    "n_lines": 30,
    }


LOG_REPLACE_ITEMS = [
    ["CRITICAL", "<span class='log-highlight critical'>CRITICAL</span>"],
    ["ERROR", "<span class='log-highlight error'>ERROR</span>"],
    ["WARNING", "<span class='log-highlight warning'>WARNING</span>"],
    ["INFO", "<span class='log-highlight info'>INFO</span>"],
    ["DEBUG", "<span class='log-highlight debug'>DEBUG</span>"],
    ["\\|", "<span class='pipe-colored log-pipe'>|</span>"],
    ]


LOG_ARGS = {
    "data_args": LOG_DATA_ARGS,
    "replace_items": LOG_REPLACE_ITEMS,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SECONDS,
    }


MAINPAGE_BLOCKS = (
    ("dashboard", STATUS_DASHBOARD_METADATA, STATUS_DASHBOARD_ARGS),
    ("table", RAW_OUTPUT_METADATA, RAW_OUTPUT_ARGS),
    ("text", LOG_METADATA, LOG_ARGS),
    )
