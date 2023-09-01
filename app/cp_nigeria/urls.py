from django.urls import path, re_path
from .views import *

urlpatterns = [
    path("", home_cpn, name="home_cpn"),
    # steps
    path("<int:proj_id>/edit/step/<int:step_id>", cpn_steps, name="cpn_steps"),
    path(
        "<int:proj_id>/edit/<int:scen_id>/step/<int:step_id>",
        cpn_steps,
        name="cpn_steps",
    ),
    path("<int:proj_id>/edit/create", cpn_scenario_create, name="cpn_scenario_create"),
    path("<int:proj_id>/edit/submit", cpn_scenario_create, name="cpn_scenario_create"),
    path("<int:proj_id>/edit/create/solar", get_pv_output, name="get_pv_output"),
    path("<int:proj_id>/edit/demand", cpn_demand_params, name="cpn_scenario_demand"),
    path("<int:proj_id>/edit/constraints", cpn_constraints, name="cpn_constraints"),
    path(
        "<int:proj_id>/edit/scenario/<int:scen_id>", cpn_scenario, name="cpn_scenario"
    ),
    path("<int:proj_id>/review/<int:scen_id>", cpn_review, name="cpn_review"),
    # path("<int:proj_id>/update/energy/system/<int:scen_id>", update_energy_system, name="update_energy_system"),
    path("ajax/usergroup/form", ajax_usergroup_form, name="ajax_usergroup_form"),
]
