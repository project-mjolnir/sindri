"""
Configuration for the plots and tables on the Mjolnir website.
"""

# Standard library imports
import datetime

# Third party imports
import pandas as pd

# Local imports
from sindri.utils.misc import WEBSITE_UPDATE_INTERVAL_S as UPDATE_INT
from sindri.website.templates import (
    GAUGE_PLOT_UPDATE_CODE,
    GAUGE_PLOT_UPDATE_CODE_VALUE,
    GAUGE_PLOT_UPDATE_CODE_COLOR,
)


STATUS_UPDATE_INTERVAL_SECONDS = 10
STATUS_UPDATE_INTERVAL_FAST_SECONDS = 1
STATUS_UPDATE_INTERVAL_SLOW_SECONDS = 20

THEME_FG_COLOR = "white"
THEME_BG_ACCENT_COLOR = "#333333"

STANDARD_COL_CONVERSIONS = {
    "runtime": (1 / (60 * 60), 2),
    "bytes_read": (1 / 1e9, 2),
    "bytes_written": (1 / 1e9, 2),
    "bytes_remaining": (1 / 1e9, 2),
}


# --- Pretty-print name map ---

VARIABLE_NAME_MAP = {
    "runtime": "Brokkr Uptime",
    "adc_vb_f": "Batt Voltage",
    "adc_va_f": "Array Voltage",
    "power_out": "Charge Power",
    "vb_ref": "Target Voltage",
    "power_load": "Load Power",
    "t_batt": "Battery Temp",
    "led_state": "LED State",
    "ping": "Ping Error Code",
    "trigger_rate_5min": "Triggers/Min",
    "crc_errors_hourly": "CRC Errors/Hr",
    "crc_errors_daily": "CRC Errors/Day",
    "bytes_written": "Data Written",
    "triggers_remaining": "Triggers Left",
    }


# --- Layout map ---

STANDARD_LAYOUTS = {
    "uptime": {"dtick": 120, "range": [0, 15 * 24], "suffix": " h"},
    "ping": {"dtick": 1, "range": [0, 2], "suffix": ""},
    "battery_voltage": {"dtick": 1, "range": [10, 15], "suffix": " V"},
    "array_voltage": {"dtick": 10, "range": [0, 50], "suffix": " V"},
    "charge_current": {"dtick": 3, "range": [0, 12], "suffix": " A"},
    "load_current": {"dtick": 0.5, "range": [0, 2.5], "suffix": " A"},
    "temperature": {"dtick": 20, "range": [-20, 80], "suffix": "°C"},
    "charge_state": {"dtick": 1, "range": [0, 8], "suffix": ""},
    "array_fault": {"dtick": 128, "range": [0, 512], "suffix": ""},
    "load_state": {"dtick": 1, "range": [0, 5], "suffix": ""},
    "load_fault": {"dtick": 32, "range": [0, 128], "suffix": ""},
    "alarm": {"dtick": 65536, "range": [0, 262144], "suffix": ""},
    "led_state": {"dtick": 2, "range": [0, 10], "suffix": ""},
    "power_out": {"dtick": 50, "range": [0, 150], "suffix": " W"},
    "power_load": {"dtick": 10, "range": [0, 30], "suffix": " W"},
    "crc_errors": {"dtick": 25, "range": [0, 100], "suffix": ""},
    "crc_errors_delta": {"dtick": 1, "range": [0, 5], "suffix": ""},
    "crc_errors_hourly": {"dtick": 5, "range": [0, 10], "suffix": ""},
    "trigger_rate": {"dtick": 20, "range": [0, 60], "suffix": ""},
    "gigabytes": {"dtick": 100, "range": [0, 500], "suffix": " GB"},
    "triggers_remaining": {"dtick": 6000, "range": [0, 24000], "suffix": ""},
    }

LAYOUT_MAP = {
    "runtime": STANDARD_LAYOUTS["uptime"],
    "ping": STANDARD_LAYOUTS["ping"],
    "adc_vb_f": STANDARD_LAYOUTS["battery_voltage"],
    "adc_va_f": STANDARD_LAYOUTS["array_voltage"],
    "adc_ic_f": STANDARD_LAYOUTS["charge_current"],
    "adc_il_f": STANDARD_LAYOUTS["load_current"],
    "t_batt": STANDARD_LAYOUTS["temperature"],
    "charge_state": STANDARD_LAYOUTS["charge_state"],
    "array_fault": STANDARD_LAYOUTS["array_fault"],
    "vb_ref": STANDARD_LAYOUTS["battery_voltage"],
    "load_state": STANDARD_LAYOUTS["load_state"],
    "load_fault": STANDARD_LAYOUTS["load_fault"],
    "alarm": STANDARD_LAYOUTS["alarm"],
    "led_state": STANDARD_LAYOUTS["led_state"],
    "power_out": STANDARD_LAYOUTS["power_out"],
    "power_load": STANDARD_LAYOUTS["power_load"],
    "sensor_uptime": STANDARD_LAYOUTS["uptime"],
    "crc_errors": STANDARD_LAYOUTS["crc_errors"],
    "crc_errors_delta": STANDARD_LAYOUTS["crc_errors_delta"],
    "crc_errors_hourly": STANDARD_LAYOUTS["crc_errors_hourly"],
    "crc_errors_daily": STANDARD_LAYOUTS["crc_errors"],
    "trigger_rate_1min": STANDARD_LAYOUTS["trigger_rate"],
    "trigger_rate_5min": STANDARD_LAYOUTS["trigger_rate"],
    "trigger_rate_1hr": STANDARD_LAYOUTS["trigger_rate"],
    "bytes_written": STANDARD_LAYOUTS["gigabytes"],
    "triggers_remaining": STANDARD_LAYOUTS["triggers_remaining"],
    }


# --- Color tables  ---

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
    "load_current": [[0.1, 0.4, 0.6, 0.7, 1.5, 1.7, 1.8, 1.9],
                     STANDARD_COLORS[::-1] + STANDARD_COLORS[1:]],
    "temperature": [[-10, 0, 10, 40, 50, 60, 70], STANDARD_COLORS_TEMP],
    "charge_state": [[i + 0.5 for i in range(8)],
                     ["gray", "blue", "maroon", "orange", "red",
                      "yellow", "lime", "green", "teal"]],
    "reference_voltage": [[12.5, 12.8, 13.0, 13.1, 14.3, 14.4, 14.6, 15.0],
                          STANDARD_COLORS[::-1] + STANDARD_COLORS[1:]],
    "load_state": [[i + 0.5 for i in range(5)],
                   ["gray", "green", "yellow", "orange", "red", "maroon"]],
    "alarm": [[-0.5, 0.5, 500], ["red", "green", "lime", "red"]],
    "led_state": [[-0.5, 2.5, 6.5, 8.5],
                  ["red", "gray", "green", "yellow", "red"]],
    "power_out": [[0.1, 6, 12, 24], STANDARD_COLORS[::-1]],
    "power_load": [[1, 6, 9, 10, 15.5, 18, 19, 20, 24],
                   STANDARD_COLORS[::-1] + ["teal"] + STANDARD_COLORS[1:]],
    "sensor_restarts": [[0.5, 1.5, 4.5, 24.5], STANDARD_COLORS],
    "crc_errors": [[0.98, 5, 12.5, 50], STANDARD_COLORS],
    "crc_errors_delta": [[0.1, 0.9, 1.5, 2.5], STANDARD_COLORS],
    "crc_errors_hourly": [[0.98, 2.5, 4.5, 8.5], STANDARD_COLORS],
    "valid_packets": [[0.5, 1.5, 2.5, 4.5], STANDARD_COLORS[::-1]],
    "triggers_daily": [[10, 500, 1000, 2000, 4000, 8000, 16000],
                       STANDARD_COLORS_TEMP],
    "trigger_rate": [[0.4, 1.4, 3, 6, 15, 30, 49], STANDARD_COLORS_TEMP],
    "triggers_remaining": [[60, 2000, 5000, 10000], STANDARD_COLORS[::-1]],
    "bytes_used": [[0.01, 0.03, 0.05, 0.11], STANDARD_COLORS[::-1]],
    "bytes_remaining": [[n * 0.022 for n in [60, 2000, 5000, 10000]],
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
    "vb_ref": STANDARD_COLOR_TABLES["reference_voltage"],
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
    "trigger_rate_1hr": STANDARD_COLOR_TABLES["trigger_rate"],
    "bytes_read": STANDARD_COLOR_TABLES["bytes_used"],
    "bytes_written": STANDARD_COLOR_TABLES["bytes_used"],
    "bytes_remaining": STANDARD_COLOR_TABLES["bytes_remaining"],
    "triggers_remaining": STANDARD_COLOR_TABLES["triggers_remaining"],
    }

COLOR_TABLE_MAP_ARCHIVE = {
    "Rsrt": STANDARD_COLOR_TABLES["sensor_restarts"],
    "NAs": STANDARD_COLOR_TABLES["crc_errors"],
    "Vbat": STANDARD_COLOR_TABLES["battery_voltage"],
    "Pin": STANDARD_COLOR_TABLES["power_out"],
    "Pout": STANDARD_COLOR_TABLES["power_load"],
    "Tmax": STANDARD_COLOR_TABLES["temperature"],
    "Ntrg": STANDARD_COLOR_TABLES["triggers_daily"],
    "Ncrc": STANDARD_COLOR_TABLES["crc_errors"],
    "Gbyt": STANDARD_COLOR_TABLES["bytes_remaining"],
    }


# --- Status dashboard section ---

STATUS_DASHBOARD_PLOTS = {
    "weblatency": {
        "plot_type": None,
        "plot_data": {},
        "plot_metadata": {
            "plot_title": "Website Latency",
            "plot_description": "",
            },
        "plot_params": {
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": 0,
            "plot_mode": "gauge+number+delta",
            "delta_reference": UPDATE_INT,
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": UPDATE_INT / 2,
            "range": [0, UPDATE_INT * 2],
            "steps": ([UPDATE_INT + ((i + 1) * 60)
                       for i in range(len(STANDARD_COLORS) - 1)],
                      STANDARD_COLORS),
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
            "suffix": " s",
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": 60,
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": 60,
            "range": [0, 300],
            "steps": ([60, 90, 120, 240], STANDARD_COLORS),
            "threshold_thickness": 0.75,
            "threshold_value": 60,
            "number_color": THEME_FG_COLOR,
            "suffix": " s",
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "blue",
            "increasing_color": "orange",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "blue",
            "increasing_color": "orange",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_title": "Triggers Per Minute",
            "plot_description": "",
            },
        "plot_params": {
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "blue",
            "increasing_color": "orange",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "red",
            "increasing_color": "green",
            "steps": None,
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
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
            "plot_fgcolor": THEME_FG_COLOR,
            "gauge_value": "NaN",
            "plot_mode": "gauge+number+delta",
            "delta_reference": "NaN",
            "decreasing_color": "green",
            "increasing_color": "red",
            "dtick": 20,
            "range": [0, 100],
            "steps": STANDARD_COLOR_TABLES["crc_errors"],
            "threshold_thickness": 0.75,
            "threshold_value": 0,
            "number_color": THEME_FG_COLOR,
            "suffix": "",
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
    "layout_map": LAYOUT_MAP,
    "color_map": COLOR_TABLE_MAP,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SECONDS,
    "update_interval_fast_seconds": (
        STATUS_UPDATE_INTERVAL_FAST_SECONDS),
    }


# --- Raw data output table section ---

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
    "col_conversions": STANDARD_COL_CONVERSIONS,
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
    "axis_name": "row",
    "color_map": COLOR_TABLE_MAP,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SECONDS,
    }


# --- Log section ---
LOG_REPLACE_ITEMS = [
    ["CRITICAL", "<span class='log-highlight critical'>CRITICAL</span>"],
    ["ERROR", "<span class='log-highlight error'>ERROR</span>"],
    ["WARNING", "<span class='log-highlight warning'>WARNING</span>"],
    ["INFO", "<span class='log-highlight info'>INFO</span>"],
    ["DEBUG", "<span class='log-highlight debug'>DEBUG</span>"],
    ["\\|", "<span class='pipe-colored log-pipe'>|</span>"],
    ]

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

LOG_ARGS = {
    "data_args": LOG_DATA_ARGS,
    "replace_items": LOG_REPLACE_ITEMS,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SECONDS,
    }


# --- Archive data table section ---

ARCHIVE_METADATA = {
    "section_id": "archive",
    "section_title": "Data Archive",
    "section_description": (
        "Summary of archival status data from the last 30 days."),
    "section_nav_label": "Archive",
    "button_content": "",
    "button_type": "",
    "button_link": "",
    "button_position": "",
    "button_newtab": "",
    }

ARCHIVE_DATA_ARGS = {
    "time_period": "30D",
    "drop_cols": ("time", "timestamp"),
    "col_conversions": STANDARD_COL_CONVERSIONS,
    "preprocess_fn": lambda full_data: full_data.groupby(
        full_data.index.date, sort=False),
    "output_cols": (
        lambda full_data: full_data["sequence_count"].agg(
            lambda full_data: full_data.diff(1).clip(lower=-1,
                                                     upper=0).sum() * -1),
        lambda full_data: full_data["sequence_count"].agg(
            lambda full_data: pd.isna(full_data).sum()),
        lambda full_data: full_data["adc_vb_f"].min(),
        lambda full_data: full_data["power_out"].mean(),
        lambda full_data: full_data["power_load"].mean(),
        lambda full_data: full_data["t_batt"].max(),
        lambda full_data: full_data["trigger_delta"].sum(),
        lambda full_data: full_data["crc_errors_delta"].sum(),
        lambda full_data: round(full_data["bytes_remaining"].min()),
        ),
    "sort_rows": False,
    "reset_index": True,
    "index_tostr": True,
    "final_colnames": ["Date", "Rsrt", "NAs", "Vbat", "Pin", "Pout", "Tmax",
                       "Ntrg", "Ncrc", "Gbyt"],
    "output_args": {
        "double_precision": 1, "date_format": "iso", "date_unit": "s"},
}

ARCHIVE_ARGS = {
    "data_args": ARCHIVE_DATA_ARGS,
    "axis_name": "column",
    "color_map": COLOR_TABLE_MAP_ARCHIVE,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SECONDS,
    }


# --- History plot section ---

HISTORY_PLOT_SUBPLOTS = {
    "runtime": {},
    "adc_vb_f": {},
    "adc_va_f": {},
    "power_out": {},
    "vb_ref": {},
    "charge_state": {},
    "power_load": {},
    "load_state": {},
    "t_batt": {},
    "led_state": {},
    "ping": {},
    "sensor_uptime": {},
    "trigger_rate_5min": {},
    "crc_errors_hourly": {},
    "crc_errors_daily": {},
    "bytes_written": {},
    "triggers_remaining": {},
}

HISTORY_PLOT_METADATA = {
    "section_id": "plots",
    "section_title": "History Plot",
    "section_description": "Plots of recorded data over time.",
    "section_nav_label": "Plots",
    "button_content": "",
    "button_type": "",
    "button_link": "",
    "button_position": "",
    "button_newtab": "",
    }

HISTORY_PLOT_DATA_ARGS = {
    "time_period": "7D",
    "decimate": 1,
    "col_conversions": STANDARD_COL_CONVERSIONS,
    "round_floats": 3,
    "index_converter": lambda index: index.strftime("%Y-%m-%d %H:%M:%S")
}

HISTORY_PLOT_CONTENT_ARGS = {
    "plot_bgcolor": THEME_BG_ACCENT_COLOR,
    "plot_fgcolor": THEME_FG_COLOR,
    "plot_height": 2048,
    "plot_margin": {"l": 0, "r": 0, "b": 0, "t": 0},
    "plot_title": "",
    "x_variable": "time",
    "xaxis_type": "date",
    "y_gap": 0.1,
    }

HISTORY_PLOT_ARGS = {
    "data_args": HISTORY_PLOT_DATA_ARGS,
    "content_args": HISTORY_PLOT_CONTENT_ARGS,
    "plot_subplots": HISTORY_PLOT_SUBPLOTS,
    "name_map": VARIABLE_NAME_MAP,
    "layout_map": LAYOUT_MAP,
    "color_map": COLOR_TABLE_MAP,
    "update_interval_seconds": STATUS_UPDATE_INTERVAL_SLOW_SECONDS,
    }


# --- Mainpage blocks ---

MAINPAGE_BLOCKS = (
    ("dashboard", STATUS_DASHBOARD_METADATA, STATUS_DASHBOARD_ARGS),
    ("table", RAW_OUTPUT_METADATA, RAW_OUTPUT_ARGS),
    ("plot", HISTORY_PLOT_METADATA, HISTORY_PLOT_ARGS),
    ("text", LOG_METADATA, LOG_ARGS),
    ("table", ARCHIVE_METADATA, ARCHIVE_ARGS),
    )
