from django.urls import path, re_path
from .views import *

urlpatterns = [
    path(
        "scenario/results/visualize",
        scenario_visualize_results,
        name="scenario_visualize_results",
    ),
    path(
        "scenario/results/visualize/<int:scen_id>",
        scenario_visualize_results,
        name="scenario_visualize_results",
    ),
    path(
        "project/<int:proj_id>/scenario/<int:scen_id>/results/visualize",
        scenario_visualize_results,
        name="scenario_visualize_results",
    ),
    path(
        "project/<int:proj_id>/scenario/results/visualize",
        scenario_visualize_results,
        name="project_visualize_results",
    ),
    path(
        "project/<int:proj_id>/scenario/results/compare",
        project_compare_results,
        name="project_compare_results",
    ),
    path("result-change-project", result_change_project, name="result_change_project"),
    path(
        "project/<int:proj_id>/scenario/results/sensitivity-analysis",
        project_sensitivity_analysis,
        name="project_sensitivity_analysis",
    ),
    path(
        "project/<int:proj_id>/scenario/results/sensitivity-analysis/<int:sa_id>",
        project_sensitivity_analysis,
        name="project_sensitivity_analysis",
    ),
    path(
        "project/<int:proj_id>/scenario/results/sensitivity-analysis/add-graph",
        sensitivity_analysis_create_graph,
        name="sensitivity_analysis_create_graph",
    ),
    path(
        "ajax/sensitivity-analysis/graph-parameters",
        ajax_get_sensitivity_analysis_parameters,
        name="ajax_get_sensitivity_analysis_parameters",
    ),
    path(
        "scenario/results/available/<int:scen_id>",
        scenario_available_results,
        name="scenario_available_results",
    ),
    path(
        "scenario/results/request_economic_data/<int:scen_id>",
        scenario_economic_results,
        name="scenario_economic_results",
    ),
    re_path(
        r"^asset/view_form/(?P<scen_id>\d+)/(?P<asset_type_name>\w+)?(/(?P<asset_uuid>[0-9a-f-]+))?$",
        view_asset_parameters,
        name="view_asset_parameters",
    ),
    path(
        "project/<int:proj_id>/scenario/results/request_kpi_table",
        request_kpi_table,
        name="request_kpi_table",
    ),
    re_path(
        r"^project/(?P<proj_id>\d+)/scenario/results/update-selected-single-scenario/(?P<scen_id>\d+)?$",
        update_selected_single_scenario,
        name="update_selected_single_scenario",
    ),
    re_path(
        r"^project/(?P<proj_id>\d+)/scenario/results/update-selected-multi-scenarios$",
        update_selected_multi_scenarios,
        name="update_selected_multi_scenarios",
    ),
    re_path(
        r"^project/(?P<proj_id>\d+)/scenario/results/request_timeseries/(?P<scen_id>\d+)?$",
        scenario_visualize_timeseries,
        name="scenario_visualize_timeseries",
    ),
    re_path(
        r"^scenario/results/request_stacked_timeseries/(?P<scen_id>\d+)?$",
        scenario_visualize_stacked_timeseries,
        name="scenario_visualize_stacked_timeseries",
    ),
    re_path(
        r"^scenario/results/request_cpn_stacked_timeseries/(?P<scen_id>\d+)?$",
        scenario_visualize_cpn_stacked_timeseries,
        name="scenario_visualize_cpn_stacked_timeseries",
    ),
    re_path(
        r"^scenario/results/request_sankey/(?P<scen_id>\d+)?$",
        scenario_visualize_sankey,
        name="scenario_visualize_sankey",
    ),
    re_path(
        r"^project/(?P<proj_id>\d+)/scenario/results/request-capacities/(?P<scen_id>\d+)?$",
        scenario_visualize_capacities,
        name="scenario_visualize_capacities",
    ),
    re_path(
        r"^project/(?P<proj_id>\d+)/scenario/results/request-costs/(?P<scen_id>\d+)?$",
        scenario_visualize_costs,
        name="scenario_visualize_costs",
    ),
    re_path(
        r"^scenario/results/request_cash_flow/(?P<scen_id>\d+)?$",
        scenario_visualize_cash_flow,
        name="scenario_visualize_cash_flow",
    ),
    re_path(
        r"^scenario/results/request_revenue/(?P<scen_id>\d+)?$",
        scenario_visualize_revenue,
        name="scenario_visualize_revenue",
    ),
    re_path(
        r"^scenario/results/request_capex/(?P<scen_id>\d+)?$",
        scenario_visualize_capex,
        name="scenario_visualize_capex",
    ),
    path(
        "scenario/results/download_scalars/<int:scen_id>",
        download_scalar_results,
        name="download_scalar_results",
    ),
    path(
        "scenario/results/download_costs/<int:scen_id>",
        download_cost_results,
        name="download_cost_results",
    ),
    path(
        "scenario/results/download_timeseries/<int:scen_id>",
        download_timeseries_results,
        name="download_timeseries_results",
    ),
    path(
        "project/<int:proj_id>/scenario/results/download_timeseries",
        redirect_download_timeseries_results,
        name="redirect_download_timeseries_results",
    ),
    path(
        "project/<int:proj_id>/scenario/results/add_graph",
        report_create_item,
        name="report_create_item",
    ),
    path(
        "project/<int:proj_id>/scenario/results/delete_graph",
        report_delete_item,
        name="report_delete_item",
    ),
    path(
        "ajax/get-graph-parameters-form/<int:proj_id>",
        ajax_get_graph_parameters_form,
        name="ajax_get_graph_parameters_form",
    ),
]
