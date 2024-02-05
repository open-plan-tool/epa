// TODO enable translation support

var timeseriesFlowTitle = "Energy flow";
var timeseriesTimeTitle = "Time";
var timeseriesCapacityTitle = "Capacity";
var timeseriesChargeDischargeTitle = "Charge/discharge";



function addReportItemGraphToDOM(parameters, reportDOMId="report_items"){

// todo: use DOMsanitize to counter XSS

    const graphId = parameters.id + "_plot";

    // generate html elements of a graph area
    var newReportItemDOM = ml("div", { id: parameters.id, class: "chart", style: "height: fit-content;"}, [
            ml("div", { class: "chart__header"}, [
                ml("div", {}, [
                    ml("span", { class: "title"}, parameters.title)
                ]),
                ml("div", { class: "dropdown"}, [
                    ml("button", { class: "btn dropdown-toggle btn--transparent", type: "button", id: "dropdownMenuTS", 'data-bs-toggle': "dropdown", 'aria-expanded': "false"}, [
                       ml("span", { class: "icon icon-more"}, [])
                    ]),
                    ml("ul", { class: "dropdown-menu", 'aria-labelledby': "dropdownMenuTS"}, [
                        ml("li", {}, ml("a", { class: "dropdown-item", href: urlNotImplemented}, "Export as .xls")),
                        ml("li", {}, ml("a", { class: "dropdown-item", href: urlNotImplemented}, "Export as .pdf")),
                        ml("li", {}, ml("a", { class: "dropdown-item", href: urlCopyReportItem}, "Copy item")),
                        ml("li", {}, ml("button", { class: "dropdown-item", onclick: deleteReportItem, "data-report-item-id": parameters.id }, "Delete item")),
                    ]),
                ]),
            ]),
            ml("div", { class: "chart__plot"}, ml("div", {id: graphId}, [])),
        ]
    );

    // append the graph to the DOM
    document.getElementById(reportDOMId).appendChild(newReportItemDOM);

    return graphId

};



// credits: https://idiallo.com/javascript/create-dom-elements-faster
function ml(tagName, props, nest) {
    var el = document.createElement(tagName);
    if(props) {
        for(var name in props) {
            if(name.indexOf("on") === 0) {
                el.addEventListener(name.substr(2).toLowerCase(), props[name], false)
            } else {
                el.setAttribute(name, props[name]);
            }
        }
    }
    if (!nest) {
        return el;
    }
    return nester(el, nest)
}

// credits: https://idiallo.com/javascript/create-dom-elements-faster
function nester(el, n) {
    if (typeof n === "string") {
        var t = document.createTextNode(n);
        el.appendChild(t);
    } else if (n instanceof Array) {
        for(var i = 0; i < n.length; i++) {
            if (typeof n[i] === "string") {
                var t = document.createTextNode(n[i]);
                el.appendChild(t);
            } else if (n[i] instanceof Node){
                el.appendChild(n[i]);
            }
        }
    } else if (n instanceof Node){
        el.appendChild(n)
    }
    return el;
}

function format_trace_name(scenario_name, label, unit, compare=false){
    clean_label = (label.charAt(0).toUpperCase() + label.slice(1)).replace(/_/g, ' ');
    console.log(clean_label)
    var trace_name = clean_label + ' (' + unit + ')' ;
    if(compare == true){
        trace_name = scenario_name + ' ' + trace_name;
    }
    return trace_name;

}


function addTimeseriesGraph(graphId, parameters){
    // prepare traces in plotly format
    var data = []

    var compare = true;
    if(parameters.data.length == 1){
        compare = false;
        parameters.title = "Scenario " + parameters.data[0].scenario_name;
    }

    parameters.data.forEach(scenario => {
        scenario.timeseries.forEach(timeseries => {
            var y_vals = timeseries.value;
            if(typeof y_vals === "string"){
                y_vals = JSON.parse(y_vals)
            }
            var trace = {x: scenario.timestamps,
                y: y_vals,
                name:"",
                type: 'scatter',
                line: {shape: 'hv'},
            };
            trace.name = format_trace_name(scenario.scenario_name, timeseries.label, timeseries.unit, compare=compare);
            data.push(trace);
        });
    });
    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,
        xaxis:{
            title: parameters.x_label,
        },
        yaxis:{
            title: parameters.y_label,
        },
        showlegend: true,
        hovermode:'x unified'
    }
    // create plot
    Plotly.newPlot(graphId, data, layout);
};

function addStackedTimeseriesGraph(graphId, parameters){
    // prepare stacked traces in plotly format
    var data = []

    if(parameters.data.length == 1){
        compare = false;
        parameters.title = parameters.title + " sector of scenario " + parameters.data[0].scenario_name;
    }

    parameters.data.forEach(scenario => {
        scenario.timeseries.forEach(timeseries => {
            // todo provide a function to format the name of the timeseries
            var trace = {x: scenario.timestamps,
                y: timeseries.value,
                name: '',
                type: 'scatter',
                line: {shape: 'hv'},
                stackgroup: timeseries.group,
                fill: timeseries.fill,
                mode: timeseries.mode,

            };
            trace.name = format_trace_name(scenario.scenario_name, timeseries.label, timeseries.unit, compare=compare);
            data.push(trace);
        });
    });
    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,
        xaxis:{
            title: parameters.x_label,
        },
        yaxis:{
            title: parameters.y_label,
        },
        hovermode:'x unified'
    }
    // create plot
    Plotly.newPlot(graphId, data, layout);
};

function storageResultGraph(x, ts_data, plot_id="",userLayout=null){

    // get the handle of the plotly plot
    if(plot_id == ""){
        plot_id = PLOT_ID;
    }
    var plotDiv = document.getElementById(plot_id);
    /* if the timestamps from the scenario are available, loads them
    var ts_timestamps_div = document.getElementById("input_timeseries_timestamps");
    if (ts_timestamps_div){
        var ts_timestamps = JSON.parse(ts_timestamps_div.querySelector("textarea").value);
        x = ts_timestamps
    }
    */

    // TODO add two y axis, one for charge/discharge and the other for SoC

    var plotLayout = {
        height: 220,
        margin:{
            b:45,
            l:60,
            r:60,
            t:15,
        },
        xaxis:{
            type: "date",
            title: timeseriesFlowTitle,
            autorange: "true",
        },
        yaxis:{
            title: timeseriesChargeDischargeTitle,
            autorange: "true",
        },
        yaxis2:{
            title: timeseriesCapacityTitle ,
            overlaying: "y",
            side: "right",
            autorange: "true",
        },
        legend: {orientation: "h"},
    };
    plotLayout = {...plotLayout, ...userLayout};
    var traces = [];
    var plot_y_axis = "y";
    for(var i=0; i<ts_data.length;++i){
        console.log(ts_data[i])
    // change legend layout
        plot_y_axis = (ts_data[i].name.includes("capacity") ? "y2" : "y");
        traces.push({type: "scatter", x: x, y: ts_data[i].value, name: ts_data[i].name + "(" + ts_data[i].unit + ")", yaxis: plot_y_axis});
    }

    Plotly.newPlot(plotDiv, traces, plotLayout, config);
    // simulate a click on autoscale
    plotDiv.querySelector('[data-title="Autoscale"]').click()
};

function plotTimeseries(x, ts_data, plot_id="",userLayout=null){

    // get the handle of the plotly plot
    if(plot_id == ""){
        plot_id = PLOT_ID;
    }
    var plotDiv = document.getElementById(plot_id);

    var plotLayout = {
        height: 220,
        margin:{
            b:45,
            l:60,
            r:60,
            t:15,
        },
        xaxis:{
            type: "date",
            title: timeseriesTimeTitle,
            autorange: "true",
        },
        yaxis:{
            title: timeseriesFlowTitle,
            autorange: "true",
        },
        legend: {orientation: "h"},
    };
    plotLayout = {...plotLayout, ...userLayout};
    var traces = [];
    var plot_y_axis = "y";
    var trace_label = "";
    for(var i=0; i<ts_data.length;++i){
        trace_label = "";
        console.log(ts_data[i]);
        if(ts_data[i].name){
            trace_label = ts_data[i].name;
            if(ts_data[i].unit){
                trace_label += "(" + ts_data[i].unit + ")";
            }
        };
        traces.push({type: "scatter", x: x, y: ts_data[i].value, name: trace_label , yaxis: plot_y_axis, ...ts_data[i].options});
    }

    Plotly.newPlot(plotDiv, traces, plotLayout, config);
    // simulate a click on autoscale
    plotDiv.querySelector('[data-title="Autoscale"]').click()
};



function addCapacitiyGraph(graphId, parameters){
    // prepare traces in ploty format
    var data = []
    // source of the palette: https://colorswall.com/palette/171311
    const colors = ["#d64e12", "#8bd346",  "#16a4d8",  "#efdf48", "#9b5fe0" , "#f9a52c", "#60dbe8"];
    const n_colors = colors.length;
    parameters.data.forEach((scenario,j) => {
        scenario.timeseries.forEach((timeseries,i) => {
            // todo provide a function to format the name of the timeseries
            data.push({
                x: scenario.timestamps,
                y: timeseries.capacity,
                name:timeseries.name,
                type: 'bar',
                offsetgroup: scenario.scenario_id,
                base: i==0 ? null : scenario.timeseries[0].capacity,
                marker: {color:colors[j%n_colors], pattern:{shape: i==0 ? "x" : ""}}

            })
        });
    });

    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,
        xaxis:{
            title: parameters.x_label,
        },
        yaxis:{
            title: parameters.y_label,
        },
        showlegend: true,
        margin: {b: 150}
    }
    // create plot
    Plotly.newPlot(graphId, data, layout);
};


function addCostGraph(graphId, parameters){
    // prepare traces in ploty format
    var data = []
    // source of the palette: https://colorswall.com/palette/171311
    const colors = ["#d64e12", "#8bd346",  "#16a4d8",  "#efdf48", "#9b5fe0" , "#f9a52c", "#60dbe8"];
    const patterns = ["", ".", "/", "x", "+", "-"]
    const n_colors = colors.length;
    parameters.data.forEach((scenario,j) => {
        scenario.timeseries.forEach((timeseries,i) => {
            // todo provide a function to format the name of the timeseries
            data.push({
                x: scenario.timestamps,
                y: timeseries.value,
                name:timeseries.name,
                text: timeseries.text,
                type: 'bar',
                offsetgroup: scenario.scenario_id,
                base: timeseries.base,
                marker: {color:colors[j%n_colors], pattern:{shape: patterns[i%6]}},
                customdata: timeseries.customdata,
                hovertemplate:timeseries.hover,
            })
        });
    });

    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,

        xaxis:{
            title: parameters.x_label,
        },
        yaxis:{
            title: parameters.y_label,
        },
        showlegend: true,
        margin: {b: 150}
    }
    // create plot
    Plotly.newPlot(graphId, data, layout);
};


function addCostScenariosGraph(graphId, parameters){
    // prepare traces in ploty format
    var data = []
    // source of the palette: https://colorswall.com/palette/171311
    const colors = ["#d64e12", "#8bd346",  "#16a4d8",  "#efdf48", "#9b5fe0" , "#f9a52c", "#60dbe8"];
    const patterns = ["", ".", "/", "x", "+", "-"]
    const n_colors = colors.length;
    //parameters.data.forEach((scenario,j) => {
    parameters.data.forEach((timeseries,j) => {
//    console.log(scenario);
//        scenario.timeseries.forEach((timeseries,i) => {
            // todo provide a function to format the name of the timeseries
            data.push({
                x: timeseries.timestamps,
                //y: timeseries.value,
                y: timeseries.timeseries,
                //name:timeseries.name,
                name:timeseries.scenario_name,
               // text: timeseries.text,
                type: 'bar',
               // offsetgroup: scenario.scenario_id,
              //  base: timeseries.base,
               // marker: {color:colors[j%n_colors], pattern:{shape: patterns[i%6]}},
             //   customdata: timeseries.customdata,
              //  hovertemplate:timeseries.hover,
            })
//        });
    });

    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,
                barmode:'stack',
        xaxis:{
            title: parameters.x_label,
        },
        yaxis:{
            title: parameters.y_label,
        },
        showlegend: true,
        margin: {b: 150}
    }
    // create plot
    Plotly.newPlot(graphId, data, layout);
};

function addSankeyDiagram(graphId, parameters){
    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,
    }
    // create plot
    Plotly.newPlot(graphId, parameters.data.data, layout);
};

function addGenericPlotlyFigure(graphId, parameters){

    const fig = JSON.parse(parameters.data);
    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,
        ... fig.layout
    }
    // create plot
    Plotly.newPlot(graphId, fig.data, layout);
};


function addSensitivityAnalysisGraph(graphId, parameters){
    // prepare graph layout in plotly format
    const layout= {
        title: parameters.title,
        xaxis:{
            title: parameters.x_label,
        },
        yaxis:{
            title: parameters.y_label,
        }
    }
    // create plot
    Plotly.newPlot(graphId, parameters.data, layout);
};

function addFinancialPlot(parameters, plot_id="") {
	var plotDiv = document.getElementById(plot_id);
	var layout = {
//        height: 220,
        margin:{
            b:100,
            l:100,
            r:100,
            t:100,
        },
        xaxis: {title: "Time"},
        yaxis: {title: "currency"},
        hovermode:'x unified',
//        legend: {orientation: "h"}
        }
    var traces = [];
    for (var i = 0; i < parameters.y.length; i++) {
    	traces.push({ type: "scatter", x: parameters.x, y: parameters.y[i], name: parameters.names[i] })
    	}
    Plotly.newPlot(plotDiv, traces, layout, config);
    // simulate a click on autoscale
    plotDiv.querySelector('[data-title="Autoscale"]').click()
}


function addPieChart(parameters, plot_id="") {
	var plotDiv = document.getElementById(plot_id);
    var labels = parameters.categories;
    var costs = parameters.costs;
    var colors = [ "B21E2A", "2168AA", "874287", "#2A8449", "CC7D00", "8C8680"]

    // Create a Plotly Pie Chart
    var data = [{
        labels: labels,
        values: costs,
        marker: {colors: colors},
        type: 'pie',
        textinfo: 'label',
        textposition: 'outside',
        automargin: true
    }];

    var layout = {
        margin:{
            'b':100,
            'l':100,
            'r':100,
            't':100,
        },
        showlegend: true,
    };

    Plotly.newPlot(plotDiv, data, layout);
}


function addCostsChart(parameters, plot_id="") {
	var plotDiv = document.getElementById(plot_id);
    var assets = parameters.assets;
    var labels = parameters.labels;
    var costs = parameters.costs;
    var data = []
    var color = "#008753";
    var patterns = ["", ".", "/", "x", "+", "-"]

    for(var i=0; i < labels.length; i++){
        var trace = {
          x: assets,
          y: costs[i],
          name: format_trace_name(labels[i]),
          type: 'bar',
          marker: {color:color, pattern:{shape: patterns[i]}}
        };
        data.push(trace)
    }

    var layout = {
        margin:{
            'b':100,
            'l':100,
            'r':100,
            't':100,
        },
        barmode: 'stack',
    };

    Plotly.newPlot(plotDiv, data, layout);
}


// TODO write functions for other report types
var graph_type_mapping={
    timeseries: addTimeseriesGraph,
    timeseries_stacked: addStackedTimeseriesGraph,
    timeseries_stacked_cpn: addStackedTimeseriesGraph,
    capacities: addCapacitiyGraph,
    costs: addCostGraph,
    costsScenarios: addCostScenariosGraph,
    sensitivity_analysis: addSensitivityAnalysisGraph,
    sankey: addSankeyDiagram,
    load_duration: addGenericPlotlyFigure
}
// # GRAPH_TIMESERIES = "timeseries"
// # GRAPH_TIMESERIES_STACKED = "timeseries_stacked"
// # GRAPH_TIMESERIES_STACKED = "timeseries_stacked_cpn"
// # GRAPH_CAPACITIES = "capacities"
// # GRAPH_BAR = "bar"
// # GRAPH_PIE = "pie"
// # GRAPH_LOAD_DURATION = "load_duration"
// # GRAPH_SANKEY = "sankey"


var existingReportItemsData = JSON.parse(document.getElementById('existingReportItemsData').textContent);
if(existingReportItemsData != "") {
    existingReportItemsData.forEach(reportItem => {
        var graphId = addReportItemGraphToDOM(reportItem);
        if (reportItem.type in graph_type_mapping) {
            graph_type_mapping[reportItem.type](graphId, reportItem);
        } else {
            console.log("the report type '" + reportItem.type + "' is not yet supported, sorry");
        }

    });
}
