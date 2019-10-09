"""
Templates and other static data for constructing the Mjolnir status website.
"""

# Standard library imports
from pathlib import Path


MAINPAGE_PATH = Path("content") / "contents.lr"


MAINPAGE_SENSOR_TEMPLATE = """
_model: single-layout
---

show_home_nav: false
---
hero_title:
---
hero_description:
---
hero_image:
---
starting_block_bg: dark
---

main_content:

{main_content}
---

"""


DASHBOARD_SECTION_TEMPLATE = """
#### dashboard ####
section_id: status
----
title: Status Dashboard
----
description: Current status of this HAMMA sensor and the Mjolnir system.
----
nav_label: Status
----
widgets:

{widgets}
----
update_script:

{update_script}

"""


DASHBOARD_ITEM_TEMPLATE = """
##### widget #####
title: {plot_title}
-----
description: {plot_description}
-----
content:

<div id="{plot_id}"></div>
-----

"""


DASHBOARD_SCRIPT_TEMPLATE = """
function convertNaN(value) {{
    if (value == -999) {{
        return NaN;
    }};
    return value;
}};

var config = {{
    editable: false,
    responsive: true,
    scrollzoom: false,
    staticplot: true,
    displayModeBar: false,
}};

var plotArray = [
    {plot_array}
]

var xmlhttp = new XMLHttpRequest()
xmlhttp.onreadystatechange = function() {{
    if (this.readyState == 4 && this.status == 200) {{
        var statusData = JSON.parse(this.responseText);
        for (plot of plotArray) {{
            plot = plot.updateFunction(statusData, plot)
            Plotly.newPlot(plot.id, plot.data, plot.layout, config);
        }};
    }}
}};

function updateStatus() {{
    xmlhttp.open('GET', '{status_json_path}', true);
    xmlhttp.send();
}};

updateStatus();
setInterval(updateStatus, {update_interval_s} * 1000);

"""


DASHBOARD_PLOT_TEMPLATE = """
{{
    id: "{plot_id}",
    data: [
        {{
            domain: {{ x: [0, 1], y: [0, 1] }},
            value: {gauge_value},
            type: "indicator",
            mode: "{plot_mode}",
            delta: {{
                decreasing: {{ color: "{decreasing_color}" }},
                increasing: {{ color: "{increasing_color}" }},
                reference: {delta_reference},
            }},
            gauge: {{
                axis: {{
                    automargin: true,
                    autotick: false,
                    dtick: {dtick},
                    range: {range},
                    tick0: {tick0},
                    tickcolor: "white",
                    tickwidth: 1,
                }},
                bar: {{ color: "cyan" }},
                bgcolor: "white",
                borderwidth: 0,
                bordercolor: "black",
                steps: [ {steps}],
                threshold: {{
                    line: {{ color: "black", width: 4 }},
                    thickness: 0.75,
                    value: {threshold_value},
                }},
            }},
            number: {{
                font: {{ color: "{number_color}" }},
                suffix: "{number_suffix}",
            }},
        }},
    ],
    layout: {{
        autosize: true,
        font: {{ color: "white" }},
        height: 200,
        margin: {{ t: 15, b: 5, l: 25, r: 25 }},
        paper_bgcolor: "rgba(0, 0, 0, 0)",
        plot_bgcolor: "rgba(0, 0, 0, 0)",
    }},
    updateFunction: function(statusData, plot) {{
        {plot_update_code}
        return plot;
    }},
}},

"""

GAUGE_PLOT_UPDATE_CODE_VALUE = """
plot.data[0].value = convertNaN(statusData.{plot_id}[0]);
plot.data[0].delta.reference = convertNaN(statusData.{plot_id}[1]);
plot.data[0].gauge.threshold.value = convertNaN(statusData.{plot_id}[2]);

"""

GAUGE_PLOT_UPDATE_CODE_COLOR = """
var foundStep = false;
for (step of plot.data[0].gauge.steps) {
    if (plot.data[0].value >= step.range[0] && plot.data[0].value <= step.range[1]) {
        plot.data[0].number.font.color = step.color;
        foundStep = true;
        break;
    };
};
if (foundStep == false) {
    plot.data[0].number.font.color = "white";
};

"""

GAUGE_PLOT_UPDATE_CODE_DEFAULT = (
    GAUGE_PLOT_UPDATE_CODE_VALUE
    + GAUGE_PLOT_UPDATE_CODE_COLOR.replace("{", "{{").replace("}", "}}"))

GAUGE_PLOT_STEPS_TEMPLATE = "{{ range: {step_range}, color: '{color}' }}, "


def generate_step_string(step_data):
    step_string = "".join((
        GAUGE_PLOT_STEPS_TEMPLATE.format(step_range=step_range, color=color)
        for step_range, color in step_data))
    return step_string
