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
section_id: {section_id}
----
title: {section_title}
----
description: {section_description}
----
nav_label: {section_nav_label}
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

<div id="{plot_id}" class="widget-container"></div>
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

var lastCheck_{section_id} = null;
var lastUpdate_{section_id} = null;
var maxLatency_{section_id} = 0;

var allPlots_{section_id} = {{
    {all_plots}
}};


Object.keys(allPlots_{section_id}).forEach(function(plotid) {{
    Plotly.newPlot(plotid, allPlots_{section_id}[plotid].data, allPlots_{section_id}[plotid].layout, config);
}});

function updatePlot(allPlots, plotid, statusData) {{
    data = allPlots[plotid].updateFunction(allPlots, plotid, statusData);
    Plotly.restyle(plotid, data);
}};


var fastUpdatePlots_{section_id} = {fast_update_plots};

function fastUpdateStatus_{section_id}() {{
    if (fastUpdatePlots_{section_id}.length > 0 && lastCheck_{section_id} != null) {{
        for (i = 0; i < fastUpdatePlots_{section_id}.length; i++) {{
            updatePlot(allPlots_{section_id}, fastUpdatePlots_{section_id}[i], null);
        }};
    }};
}};

if (fastUpdatePlots_{section_id}.length > 0) {{
    setInterval(fastUpdateStatus_{section_id}, {update_interval_fast_seconds} * 1000);
}};


var xhrUpdate_{section_id} = new XMLHttpRequest();
xhrUpdate_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var statusData = JSON.parse(this.responseText);
        Object.keys(allPlots_{section_id}).forEach(function(plotid) {{
            if (fastUpdatePlots_{section_id}.indexOf(plotid) == -1) {{
                updatePlot(allPlots_{section_id}, plotid, statusData);
            }};
        }});
    }};
}};

var xhrCheck_{section_id} = new XMLHttpRequest();
xhrCheck_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var lastUpdateData = JSON.parse(this.responseText);
        var currentCheck = new Date(lastUpdateData.lastCheck);
        if (lastCheck_{section_id} == null || lastCheck_{section_id}.getTime() != currentCheck.getTime()) {{
            lastCheck_{section_id} = new Date(lastUpdateData.lastCheck);
            fastUpdateStatus_{section_id}();
            var currentUpdate = new Date(lastUpdateData.lastUpdate);
            if (lastUpdate_{section_id} == null || lastUpdate_{section_id}.getTime() != currentUpdate.getTime()) {{
                    lastUpdate_{section_id} = currentUpdate;
                    xhrUpdate_{section_id}.open("GET", "{data_path}", true);
                    xhrUpdate_{section_id}.send();
            }};
        }};
    }};
}};

function updateStatus_{section_id}() {{
    xhrCheck_{section_id}.open("GET", "{lastupdate_path}", true);
    xhrCheck_{section_id}.send();
}};

updateStatus_{section_id}();
setInterval(updateStatus_{section_id}, {update_interval_seconds} * 1000);

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
var allSteps = allPlots[plotid].data[0].gauge.steps;
for (i = 0; i < allSteps.length; i++) {
    if (data["value"] >= allSteps[i].range[0] && data["value"] <= allSteps[i].range[1]) {
        data["number.font.color"] = allSteps[i].color;
        foundStep = true;
        break;
    };
};
if (! foundStep) {
    data["number.font.color"] = "white";
};

"""

GAUGE_PLOT_UPDATE_CODE = (GAUGE_PLOT_UPDATE_CODE_VALUE
                          + GAUGE_PLOT_UPDATE_CODE_COLOR)

GAUGE_PLOT_STEPS_TEMPLATE = "{{ range: {step_range}, color: '{color}' }}, "


CONTENT_SECTION_TEMPLATE = """
#### content ####
section_id: {section_id}
----
title: {section_title}
----
description: {section_description}
----
nav_label: {section_nav_label}
----
button_content: {button_content}
----
button_type: {button_type}
----
button_link: {button_link}
----
button_position: {button_position}
----
button_newtab: {button_newtab}
----
content:

{content}

"""

TEXT_CONTENT_TEMPLATE = """
<div id="{section_id}-container" class="content-container text-content-container">
  <code id="{section_id}-output" class="content-output text-content-output"></code>
</div>

<script>
var lastUpdate_{section_id} = null;
var replaceItems = {replace_items};
var xhrUpdate_{section_id} = new XMLHttpRequest();
xhrUpdate_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var outputText = this.responseText;
        outputText = outputText.replace(new RegExp("\\n", "g"), "\\n<br>\\n");
        for (i = 0; i < replaceItems.length; i++) {{
            var regexPattern = new RegExp(replaceItems[i][0], "g");
            outputText = outputText.replace(regexPattern, replaceItems[i][1]);
        }};
        var nodeToModify = document.getElementById("{section_id}-output");
        nodeToModify.innerHTML = outputText;
    }};
}};

var xhrCheck_{section_id} = new XMLHttpRequest();
xhrCheck_{section_id}.onreadystatechange = function() {{
    if (this.readyState == XMLHttpRequest.DONE && this.status < 300 && this.status >= 200) {{
        var lastUpdateData = JSON.parse(this.responseText);
        var currentUpdate = new Date(lastUpdateData.lastUpdate);
        if (lastUpdate_{section_id} == null || lastUpdate_{section_id}.getTime() != currentUpdate.getTime()) {{
            lastUpdate_{section_id} = currentUpdate;
            xhrUpdate_{section_id}.open("GET", "{text_path}", true);
            xhrUpdate_{section_id}.send();
        }};
    }};
}};


function updateStatus_{section_id}() {{
    xhrCheck_{section_id}.open("GET", "{lastupdate_path}", true);
    xhrCheck_{section_id}.send();
}};

updateStatus_{section_id}();
setInterval(updateStatus_{section_id}, {update_interval_seconds} * 1000);
</script>

"""


def generate_step_string(step_data):
    step_string = "".join((
        GAUGE_PLOT_STEPS_TEMPLATE.format(step_range=step_range, color=color)
        for step_range, color in step_data))
    return step_string
