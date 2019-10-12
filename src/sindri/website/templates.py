"""
Templates and other static data for constructing the Mjolnir status website.
"""


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
    if (value == {sentinel_value_json}) {{
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

var lastUpdate = null
var maxLatency = 0

var allPlots = {{
    {all_plots}
}};


Object.keys(allPlots).forEach(function(plotid) {{
    Plotly.newPlot(plotid, allPlots[plotid].data, allPlots[plotid].layout, config);
}});

function updatePlot(allPlots, plotid, statusData) {{
    data = allPlots[plotid].updateFunction(allPlots, plotid, statusData);
    Plotly.restyle(plotid, data);
}};


var fastUpdatePlots = {fast_update_plots};

function fastUpdateStatus() {{
    if (fastUpdatePlots.length > 0 && lastUpdate != null) {{
        for (plotid of fastUpdatePlots) {{
            updatePlot(allPlots, plotid, null);
        }};
    }};
}};

if (fastUpdatePlots.length > 0) {{
    setInterval(fastUpdateStatus, {update_interval_fast_s} * 1000);
}};

var xhr = new XMLHttpRequest()
xhr.onreadystatechange = function() {{
    if (this.readyState == 4 && this.status < 300 && this.status >= 200) {{
        var statusData = JSON.parse(this.responseText);
        var currentUpdate = new Date(statusData.lastupdatetimestamp);
        if (lastUpdate == null || lastUpdate != currentUpdate) {{
            if (lastUpdate == null) {{
                lastUpdate = currentUpdate;
                fastUpdateStatus();
            }};
            lastUpdate = currentUpdate;
            Object.keys(allPlots).forEach(function(plotid) {{
                if (! fastUpdatePlots.includes(plotid)) {{
                    updatePlot(allPlots, plotid, statusData);
                }};
            }});
        }};
    }};
}};

function updateStatus() {{
    xhr.open("GET", "{status_json_path}", true);
    xhr.send();
}};

updateStatus();
setInterval(updateStatus, {update_interval_s} * 1000);

"""


DASHBOARD_PLOT_TEMPLATE = """
{plot_id}: {{
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
                    thickness: {threshold_thickness},
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
        margin: {{ t: 25, b: 5, l: 25, r: 25 }},
        paper_bgcolor: "rgba(0, 0, 0, 0)",
        plot_bgcolor: "rgba(0, 0, 0, 0)",
    }},
    updateFunction: function(allPlots, plotid, statusData) {{
        data = {{}};
        {plot_update_code}
        return data;
    }},
}},

"""

GAUGE_PLOT_UPDATE_CODE_VALUE = """
data["value"] = convertNaN(statusData[plotid][0]);
data["delta.reference"] = convertNaN(statusData[plotid][1]);
data["gauge.threshold.value"] = convertNaN(statusData[plotid][2]);

"""

GAUGE_PLOT_UPDATE_CODE_COLOR = """
var foundStep = false;
for (step of allPlots[plotid].data[0].gauge.steps) {
    if (data["value"] >= step.range[0] && data["value"] <= step.range[1]) {
        data["number.font.color"] = step.color;
        foundStep = true;
        break;
    };
};
if (foundStep == false) {
    data["number.font.color"] = "white";
};

"""

GAUGE_PLOT_UPDATE_CODE = (GAUGE_PLOT_UPDATE_CODE_VALUE
                          + GAUGE_PLOT_UPDATE_CODE_COLOR)

GAUGE_PLOT_STEPS_TEMPLATE = "{{ range: {step_range}, color: '{color}' }}, "


def generate_step_string(step_data):
    step_string = "".join((
        GAUGE_PLOT_STEPS_TEMPLATE.format(step_range=step_range, color=color)
        for step_range, color in step_data))
    return step_string
