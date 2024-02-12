$(document).ready(function () {
    // add search field to the kpi info modal
    $('#kpiTable').DataTable();
    const scen_id = "{{ scen_id }}";
    const proj_id = "{{ proj_id }}";

    // load the scenario plots
    update_kpi_table_style(scen_id);
    scenario_visualize_cpn_stacked_timeseries(scen_id);
    scenario_visualize_capacities(scen_id);
//    scenario_visualize_costs(scen_id);
    scenario_visualize_cash_flow(scen_id);
    scenario_visualize_revenue(scen_id);
    scenario_visualize_system_costs(scen_id, system_costs);
    scenario_visualize_capex(scen_id);
});


// allow to collapse the dataframe tables
function collapseTables(){
    var elements = document.getElementsByClassName('chart__plot collapse show');
        for (let i = 0; i < elements.length; i++) {
            console.log(elements[i].id);
            $('#'+elements[i].id).collapse();
            }
// elements[i].addEventListener('touchstart', drag, false);)
    };


function update_selected_single_scenario(target){
    const proj_id = target.split("-")[1];
    const scen_id = target.split("-")[2];

    // call the list and the success should then call other function which collect the data in the session's cache and plot it(session cache should use mvs tokens to know if a simulation was updated or not)
    if(scen_id != null){

        $.ajax({
            url: urlUpdatedSingleScenario,
            type: "GET",
            success: async (data) => {

                /* Update the kpi table */
                update_kpi_table_style(scen_id);

                scenario_visualize_timeseries(scen_id);
                // scenario_visualize_stacked_timeseries(scen_id);
                scenario_visualize_cpn_stacked_timeseries(scen_id);
                scenario_visualize_sankey(scen_id);
                scenario_visualize_capacities(scen_id);
                scenario_visualize_costs(scen_id);
            },
            error: function (xhr, errmsg) {
                if (xhr.status != 405){
                    console.log("backend_error!")
                    //Show the error message
                    $('#message-div').html("<div class='alert-error'>" +
                        "<strong>Success: </strong> We have encountered an error: " + errmsg + "</div>");
                }
            }
        });
    }
}


// Functions to visualize tables/charts
function update_kpi_table_style(scen_id=""){

    $.ajax({
        url: urlKpiResults,
        type: "GET",
        success: async (table_data) => {

        const parentDiv = document.getElementById("selectedKPITable");
        parentDiv.innerHTML = "";


        /* create KPI table headers */
        const tableHead = document.createElement('thead');
        const table_headers = table_data.hdrs; // todo add dynamically more scenarios here
        const table_length = table_headers.length;
        const tableHeadContent = document.createElement('tr');
        table_headers.map(hdr =>
            {
                var tableHdr = document.createElement('th');
                tableHdr.innerHTML = hdr;
                tableHeadContent.appendChild(tableHdr);
            }
        );
        tableHead.appendChild(tableHeadContent)
        parentDiv.appendChild(tableHead);


        for(subBody in table_data.data) {
            var tableBody = document.createElement('tbody');
            tableBody.id = subBody;
            /* add subtable title */
            const tableSubSectionTitleRow = document.createElement('tr');
            var tableSubSectionTitle = document.createElement('th');
            tableSubSectionTitle.innerHTML = subBody;
            tableSubSectionTitleRow.appendChild(tableSubSectionTitle);
            for(i=0;i<table_length-1;++i){
                tableSubSectionTitleRow.appendChild(document.createElement('td'));
            }

            //tableBody.appendChild(tableSubSectionTitle);

            /* add subtable lines for each parameter */
            // (param should be a json object) with keys name (type str), unit type (str) and scen_values
            table_data.data[subBody].map(param =>{
                var tableSubSectionParamRow = document.createElement('tr');
                var cell = tableSubSectionParamRow.insertCell(0);
                cell.innerHTML = param.name + " (" + param.unit + `) <a data-bs-toggle="tooltip" title="" data-bs-original-title="${param.description}" data-bs-placement="right"><img style="height: 1.2rem;margin-left:.5rem" alt="info icon" src="${srcInfoIcon}"></a>`;
                //cell.setAttribute("title", param.description)
                //cell.append(" just to see");
                // todo for loop over scenario values
                for(i=0;i<param.scen_values.length;++i){
                    cell = tableSubSectionParamRow.insertCell(1 + i);
                    cell.innerHTML = param.scen_values[i]
                };
                tableBody.appendChild(tableSubSectionParamRow);
            });


            parentDiv.appendChild(tableBody);
        }
        $('[data-bs-toggle="tooltip"]').tooltip()

        },
        /*error: function (xhr, errmsg) {
            console.log("backend_error!")
            //Show the error message
            $('#message-div').html("<div class='alert-error'>" +
                "<strong>Success: </strong> We have encountered an error: " + errmsg + "</div>");
        }*/
    });

};

/* loop over scenario selection buttons and return the ids of the selected ones */
// function fetchSelectedScenarios(){
//     var selectedScenarios = [];
//     var scenariosDropDown = $("#results-scenarios");
//     if(scenariosDropDown){
// 			if(Array.isArray(scenariosDropDown.val()) == false){
// 				selectedScenarios.push(scenariosDropDown.val().split("-")[2]);
// 			}
// 			else{
// 				selectedScenarios = scenariosDropDown.val();
// 			};
//     };
//     return selectedScenarios;
// };



function scenario_visualize_timeseries(scen_id=""){
 $.ajax({
            url: urlVisualizeTimeseries,
            type: "GET",
            success: async (parameters) => {
                await graph_type_mapping[parameters.type](parameters.id, parameters);
            }
        });
};

function scenario_visualize_cpn_stacked_timeseries(scen_id){
    $.ajax({
        url: urlVisualizeStackedTimeseries,
        type: "GET",
        success: async (graphs) => {
            const parentDiv = document.getElementById("cpn_stacked_timeseries");
            await graphs.map(parameters => {
                if(parameters.id != "Gas") {
                    const newGraph = document.createElement('div');
                    newGraph.id = "cpn_stacked_timeseries" + parameters.id;
                    parentDiv.appendChild(newGraph);
                    graph_type_mapping[parameters.type](newGraph.id, parameters);
                    // TODO change plotly title here
                }
            });
        },
    });
};

//function scenario_visualize_sankey(scen_id){
// $.ajax({
//            url: "{% url 'scenario_visualize_sankey' %}" + scen_id,
//            type: "GET",
//            success: async (parameters) => {
//                await graph_type_mapping[parameters.type](parameters.id, parameters);
//            },
//        });
//};

function scenario_visualize_capacities(scen_id=""){
 $.ajax({
            url: urlVisualizeCapacities,
            type: "GET",
            success: async (parameters) => {
                await graph_type_mapping[parameters.type](parameters.id, parameters);;
            },
        });
};

//function scenario_visualize_costs(scen_id=""){
// $.ajax({
//            url: urlVisualizeCosts,
//            type: "GET",
//            success: async (graphs) => {
//                const parentDiv = document.getElementById("costs");
//                await graphs.map(parameters => {
//                    const newGraph = document.createElement('div');
//                    newGraph.id = "costs" + parameters.id;
//                    parentDiv.appendChild(newGraph);
//                    if(parameters.title === "var1" || parameters.title === "var2")
//                            { graph_type= parameters.type;
//                                parameters.title = "";}
//                            else{ graph_type = parameters.type + "Scenarios";}
//                    graph_type_mapping[graph_type](newGraph.id, parameters);
//                });
//            },
//        });
//};

function scenario_visualize_cash_flow(scen_id=""){
 $.ajax({
            url: urlVisualizeCashFlow,
            type: "GET",
            success: async (parameters) => {
                await addFinancialPlot(parameters, plot_id="cash_flow");
            },
        });
};

function scenario_visualize_revenue(scen_id=""){
 $.ajax({
            url: urlVisualizeRevenue,
            type: "GET",
            success: async (parameters) => {
                await addFinancialPlot(parameters, plot_id="revenue");
            },
        });
};

function scenario_visualize_capex(scen_id=""){
 $.ajax({
            url: urlVisualizeCapex,
            type: "GET",
            success: async (parameters) => {
                await addPieChart(parameters, plot_id="capex");
            },
        });
};

function scenario_visualize_system_costs(scen_id=""){
 $.ajax({
            url: urlVisualizeSystemCosts,
            type: "GET",
            success: async (parameters) => {
                await addCostsChart(parameters, plot_id="system_costs");
            },
        });
};



/** Add a new report item **/
function updateReportItemParametersForm(graphType){
    // Passes the existing text of the title to the form initials
    reportItemTitleDOM = createReportItemForm.querySelector('input[id="id_title"]');
    if(reportItemTitleDOM){
        reportItemTitle = reportItemTitleDOM.value
    }
    // Passes the preselected scenarios to the form initials
    reportItemScenariosDOM = createReportItemForm.querySelector('select[id="id_scenarios"]');
    if(reportItemScenariosDOM){
        reportItemScenarios = [];
        Array.from(reportItemScenariosDOM.querySelectorAll('option:checked')).forEach(item => {
            reportItemScenarios.push(item.value);
        });
    }
    else{
        reportItemScenarios = fetchSelectedScenarios();
    }

    var urlForm = createReportItemForm.getAttribute("graph-parameter-url");

    $.ajax({
        url: urlForm,
        type: "POST",
        headers: {'X-CSRFToken': '{{ csrf_token }}'},
        data: {
          'title': reportItemTitle,
          'report_type': graphType,
          'selected_scenarios': JSON.stringify(reportItemScenarios),
          'multi_scenario': multipleScenarioSelection
        },
        success: function (formData) {
           // find and keep the csrf token of the form
           var csrfToken = createReportItemForm.querySelector('input[name="csrfmiddlewaretoken"]');

            console.log(formData)

           // update the report item graph
           createReportItemForm.innerHTML = csrfToken.outerHTML + formData;

           // (re)link the changing of report_item type combobox to loading new parameters form
           // the name of the id is linked with the name of the attribute of ReportItem model in dashboard/models.py
           $("#id_report_type").change(function (event) {
                var reportItemType = $(this).val();
                updateReportItemParametersForm(reportItemType)
           })
           $("#id_scenarios").change(function (event) {
                var reportItemType = $("#id_report_type").val();
                updateReportItemParametersForm(reportItemType)
           })
        }
    });
};

function showCreateReportItemModal(event){
    showModal(
        event,
        modalId="createReportItemModal",
        attrs={
            enctype: "multipart/form-data",
            "ajax-post-url": `{% url 'report_create_item' proj_id %}`,
            "graph-parameter-url": `{% url 'ajax_get_graph_parameters_form' proj_id %}`
        }
    )
    updateReportItemParametersForm("timeseries")
    //createReportItemModal.show()

}



document.querySelectorAll("#results-analysis-links a").forEach(el => {el.classList.remove("active")});
