from django.contrib.auth.decorators import login_required
import json
import logging
import traceback
from django.http import HttpResponseForbidden, JsonResponse
from django.http.response import Http404
from jsonview.decorators import json_view
from django.utils.translation import gettext_lazy as _
from django.shortcuts import *
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from epa.settings import MVS_GET_URL, MVS_LP_FILE_URL
from .forms import *
from projects.requests import fetch_mvs_simulation_results
from projects.models import *
from projects.services import RenewableNinjas
from projects.constants import DONE, PENDING, ERROR, MODIFIED

logger = logging.getLogger(__name__)

STEP_MAPPING = {
    "choose_location": 1,
    "demand_profile": 2,
    "scenario_setup": 3,
    "economic_params": 4,
    "simulation": 5,
    "business_model": 6,
    "outputs": 7,
}

CPN_STEP_VERBOSE = {
    "choose_location": _("Choose location"),
    "demand_profile": _("Demand load profile selection"),
    "scenario_setup": _("Scenario setup"),
    "economic_params": _("Economic parameters"),
    "simulation": _("Simulation"),
    "business_model": _("Business Model"),
    "outputs": _("Outputs"),
}

# sorts the step names based on the order defined in STEP_MAPPING (for ribbon)
CPN_STEP_VERBOSE = [
    CPN_STEP_VERBOSE[k] for k, v in sorted(STEP_MAPPING.items(), key=lambda x: x[1])
]


@require_http_methods(["GET"])
def home_cpn(request):
    return render(request, "cp_nigeria/index_cpn.html")


@login_required
@require_http_methods(["GET", "POST"])
def cpn_scenario_create(request, proj_id=None, step_id=STEP_MAPPING["choose_location"]):
    qs_project = Project.objects.filter(id=proj_id)
    if qs_project.exists():
        project = qs_project.get()
        if (project.user != request.user) and (
            project.viewers.filter(
                user__email=request.user.email, share_rights="edit"
            ).exists()
            is False
        ):
            raise PermissionDenied

    else:
        project = None

    if request.method == "POST":
        if project is not None:
            form = ProjectForm(request.POST, instance=project)
        else:
            form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(user=request.user)
            return HttpResponseRedirect(
                reverse("cpn_scenario_demand", args=[project.id])
            )
    elif request.method == "GET":
        if project is not None:
            scenario = Scenario.objects.get(project=project)
            form = ProjectForm(
                instance=project, initial={"start_date": scenario.start_date}
            )
        else:
            form = ProjectForm()
    messages.info(
        request,
        "Please input basic project information, such as name, location and duration. You can "
        "input geographical data by clicking on the desired project location on the map.",
    )

    return render(
        request,
        f"cp_nigeria/steps/scenario_create.html",
        {
            "form": form,
            "proj_id": proj_id,
            "step_id": step_id,
            "step_list": CPN_STEP_VERBOSE,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def cpn_demand_params(request, proj_id, step_id=STEP_MAPPING["demand_profile"]):
    project = get_object_or_404(Project, id=proj_id)

    # TODO change DB default value to 1
    # TODO include the possibility to display the "expected_consumer_increase", "expected_demand_increase" fields
    # with option advanced_view set by user choice
    form = ConsumerGroupForm(initial={"number_consumers": 1}, advanced_view=False)

    messages.info(
        request,
        "Please input user group data. This includes user type information about "
        "households, enterprises and facilities and predicted energy demand tiers as collected from "
        "survey data or available information about the community.",
    )

    # TODO@Paula use a FormSet for the consumer groups instead of a custom made table structure

    return render(
        request,
        f"cp_nigeria/steps/scenario_demand.html",
        {
            "form": form,
            "proj_id": proj_id,
            "step_id": step_id,
            "scen_id": project.scenario.id,
            "step_list": CPN_STEP_VERBOSE,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def cpn_scenario(request, proj_id, step_id=STEP_MAPPING["scenario_setup"]):
    project = get_object_or_404(Project, id=proj_id)
    scenario = project.scenario

    if request.method == "GET":
        messages.info(
            request,
            "Select the energy system components you would like to include in the simulation. The "
            "system can be comprised of a diesel generator, a PV-system, and a battery system (storage) "
            "in any combination.",
        )

        context = {
            "proj_id": proj_id,
            "step_id": step_id,
            "scen_id": scenario.id,
            "step_list": CPN_STEP_VERBOSE,
            "es_assets": [],
        }

        asset_type_name = "bess"

        qs = Asset.objects.filter(
            scenario=scenario.id, asset_type__asset_type=asset_type_name
        )

        if qs.exists():
            existing_ess_asset = qs.get()
            ess_asset_children = Asset.objects.filter(
                parent_asset=existing_ess_asset.id
            )
            ess_capacity_asset = ess_asset_children.get(
                asset_type__asset_type="capacity"
            )
            ess_charging_power_asset = ess_asset_children.get(
                asset_type__asset_type="charging_power"
            )
            ess_discharging_power_asset = ess_asset_children.get(
                asset_type__asset_type="discharging_power"
            )
            # also get all child assets
            context["es_assets"].append(asset_type_name)
            context["form_storage"] = BessForm(
                initial={
                    "name": existing_ess_asset.name,
                    "installed_capacity": ess_capacity_asset.installed_capacity,
                    "age_installed": ess_capacity_asset.age_installed,
                    "capex_fix": ess_capacity_asset.capex_fix,
                    "capex_var": ess_capacity_asset.capex_var,
                    "opex_fix": ess_capacity_asset.opex_fix,
                    "opex_var": ess_capacity_asset.opex_var,
                    "lifetime": ess_capacity_asset.lifetime,
                    "crate": ess_capacity_asset.crate,
                    "efficiency": ess_capacity_asset.efficiency,
                    "dispatchable": ess_capacity_asset.dispatchable,
                    "optimize_cap": ess_capacity_asset.optimize_cap,
                    "soc_max": ess_capacity_asset.soc_max,
                    "soc_min": ess_capacity_asset.soc_min,
                }
            )
        else:
            context["form_bess"] = BessForm()

        for asset_type_name, form in zip(
            ["pv_plant", "diesel_generator"], [PVForm, DieselForm]
        ):
            qs = Asset.objects.filter(
                scenario=scenario.id, asset_type__asset_type=asset_type_name
            )

            if qs.exists():
                existing_asset = qs.get()
                context["es_assets"].append(asset_type_name)
                context[f"form_{asset_type_name}"] = form(instance=existing_asset)

            else:

                context[f"form_{asset_type_name}"] = form()

        return render(request, f"cp_nigeria/steps/scenario_components.html", context)
    if request.method == "POST":

        asset_forms = dict(bess=BessForm, pv_plant=PVForm, diesel_generator=DieselForm)
        print(request.POST)
        # import pdb;pdb.set_trace()
        assets = request.POST.getlist("es_choice", [])

        qs = Bus.objects.filter(scenario=scenario)

        if qs.exists():
            bus_el = qs.get()
        else:
            bus_el = Bus(
                type="Electricity",
                scenario=scenario,
                pos_x=600,
                pos_y=150,
                name="el_bus",
            )
            bus_el.save()

        for i, asset_name in enumerate(assets):
            qs = Asset.objects.filter(
                scenario=scenario, asset_type__asset_type=asset_name
            )
            if qs.exists():
                form = asset_forms[asset_name](request.POST, instance=qs.first())
            else:
                form = asset_forms[asset_name](request.POST)

            if form.is_valid():
                asset_type = get_object_or_404(AssetType, asset_type=asset_name)

                asset = form.save(commit=False)
                # TODO the form save should do some specific things to save the storage correctly

                asset.scenario = scenario
                asset.asset_type = asset_type
                asset.pos_x = 400
                asset.pos_y = 150 + i * 150
                asset.save()
                if asset_name == "bess":
                    ConnectionLink.objects.create(
                        bus=bus_el,
                        bus_connection_port="input_1",
                        asset=asset,
                        flow_direction="A2B",
                        scenario=scenario,
                    )
                    ConnectionLink.objects.create(
                        bus=bus_el,
                        bus_connection_port="output_1",
                        asset=asset,
                        flow_direction="B2A",
                        scenario=scenario,
                    )
                else:
                    ConnectionLink.objects.create(
                        bus=bus_el,
                        bus_connection_port="input_1",
                        asset=asset,
                        flow_direction="A2B",
                        scenario=scenario,
                    )

        # Remove unselected assets
        for asset in Asset.objects.filter(
            scenario=scenario.id,
            asset_type__asset_type__in=["bess", "pv_plant", "diesel_generator"],
        ):
            if asset.asset_type.asset_type not in assets:
                asset.delete()

        #     if form.is_valid():
        #         # check whether the constraint is already associated to the scenario
        #         qs = constraints_models[constraint_type].objects.filter(
        #             scenario=scenario
        #         )
        #         if qs.exists():
        #             if len(qs) == 1:
        #                 constraint_instance = qs[0]
        #                 for name, value in form.cleaned_data.items():
        #                     if getattr(constraint_instance, name) != value:
        #                         setattr(constraint_instance, name, value)
        #                         if qs_sim.exists():
        #                             qs_sim.update(status=MODIFIED)
        #
        #         else:
        #             constraint_instance = form.save(commit=False)
        #             constraint_instance.scenario = scenario
        #
        #         if constraint_type == "net_zero_energy":
        #             constraint_instance.value = constraint_instance.activated
        #
        #         constraint_instance.save()
        #
        return HttpResponseRedirect(reverse("cpn_steps", args=[proj_id, 4]))

        # import pdb;pdb.set_trace()


@login_required
@require_http_methods(["GET", "POST"])
def cpn_constraints(request, proj_id, step_id=STEP_MAPPING["economic_params"]):
    project = get_object_or_404(Project, id=proj_id)
    scenario = project.scenario
    messages.info(
        request, "Please include any relevant constraints for the optimization."
    )

    if request.method == "POST":
        form = EconomicDataForm(request.POST, instance=project.economic_data)

        if form.is_valid():
            project = form.save()
            return HttpResponseRedirect(reverse("cpn_review", args=[proj_id]))
    elif request.method == "GET":

        form = EconomicDataForm(
            instance=project.economic_data, initial={"capex_fix": scenario.capex_fix}
        )

        return render(
            request,
            f"cp_nigeria/steps/scenario_system_params.html",
            {
                "proj_id": proj_id,
                "step_id": step_id,
                "scen_id": scenario.id,
                "form": form,
                "step_list": CPN_STEP_VERBOSE,
            },
        )


@login_required
@require_http_methods(["GET", "POST"])
def cpn_review(request, proj_id, step_id=STEP_MAPPING["simulation"]):
    project = get_object_or_404(Project, id=proj_id)

    if (project.user != request.user) and (request.user not in project.viewers.all()):
        raise PermissionDenied

    if request.method == "GET":
        html_template = f"cp_nigeria/steps/simulation/no-status.html"
        context = {
            "scenario": project.scenario,
            "scen_id": project.scenario.id,
            "proj_id": proj_id,
            "proj_name": project.name,
            "step_id": step_id,
            "step_list": CPN_STEP_VERBOSE,
            "MVS_GET_URL": MVS_GET_URL,
            "MVS_LP_FILE_URL": MVS_LP_FILE_URL,
        }

        qs = Simulation.objects.filter(scenario=project.scenario)

        if qs.exists():
            simulation = qs.first()

            if simulation.status == PENDING:
                fetch_mvs_simulation_results(simulation)

            context.update(
                {
                    "sim_id": simulation.id,
                    "simulation_status": simulation.status,
                    "secondsElapsed": simulation.elapsed_seconds,
                    "rating": simulation.user_rating,
                    "mvs_token": simulation.mvs_token,
                }
            )

            if simulation.status == ERROR:
                context.update({"simulation_error_msg": simulation.errors})
                html_template = "cp_nigeria/steps/simulation/error.html"
            elif simulation.status == PENDING:
                html_template = "cp_nigeria/steps/simulation/pending.html"
            elif simulation.status == DONE:
                html_template = "cp_nigeria/steps/simulation/success.html"

        else:
            print("no simulation existing")

        return render(request, html_template, context)


# TODO for later create those views instead of simply serving the html templates
CPN_STEPS = {
    "choose_location": cpn_scenario_create,
    "demand_profile": cpn_demand_params,
    "scenario_setup": cpn_scenario,
    "economic_params": cpn_constraints,
    "simulation": cpn_review,
}

# sorts the order in which the views are served in cpn_steps (defined in STEP_MAPPING)
CPN_STEPS = [
    CPN_STEPS[k]
    for k, v in sorted(STEP_MAPPING.items(), key=lambda x: x[1])
    if k in CPN_STEPS
]


@login_required
@require_http_methods(["GET", "POST"])
def cpn_steps(request, proj_id, step_id=None):
    if step_id is None:
        return HttpResponseRedirect(reverse("cpn_steps", args=[proj_id, 1]))

    return CPN_STEPS[step_id - 1](request, proj_id, step_id)


@login_required
@require_http_methods(["GET", "POST"])
# TODO: make this view work with dynamic coordinates (from map)
def get_pv_output(request, proj_id):
    project = Project.objects.get(id=proj_id)
    coordinates = {"lat": project.latitude, "lon": project.longitude}
    location = RenewableNinjas()
    location.get_pv_output(coordinates)
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="pv_output.csv"'},
    )
    location.data.to_csv(response, index=False, sep=";")
    plot_div = location.create_pv_graph()
    # HttpResponseRedirect(reverse("home_cpn", args=[project.id]))
    return response


@login_required
@json_view
@require_http_methods(["POST"])
def ajax_consumergroup_form(request, scen_id=None, user_group_id=None):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # TODO change DB default value to 1
        # TODO include the possibility to display the "expected_consumer_increase", "expected_demand_increase" fields
        # with option advanced_view set by user choice
        form_ug = ConsumerGroupForm(
            initial={"number_consumers": 1}, advanced_view=False
        )
        return render(
            request,
            "cp_nigeria/steps/consumergroup_form.html",
            context={
                "form": form_ug,
                "scen_id": scen_id,
                "unique_id": request.POST.get("ug_id"),
            },
        )


@login_required
@json_view
@require_http_methods(["GET", "POST"])
def ajax_load_timeseries(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        consumer_type_id = request.GET.get("consumer_type")
        timeseries_qs = DemandTimeseries.objects.filter(
            consumer_type_id=consumer_type_id
        )
        return render(
            request,
            "cp_nigeria/steps/timeseries_dropdown_options.html",
            context={"timeseries_qs": timeseries_qs},
        )


@login_required
@json_view
@require_http_methods(["POST"])
def create_consumergroup(request, scen_id=None):
    # todo use redirect or use pure ajax call without redirect like for assets saving
    return {"status": 200}


@login_required
@json_view
@require_http_methods(["POST"])
def delete_consumergroup(request, scen_id=None):
    """This ajax view is triggered by clicking on "delete" in the consumergroup top right menu options"""
    return {"status": 200}


@login_required
@json_view
@require_http_methods(["POST"])
def ajax_update_graph(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        timeseries_id = request.POST.get("timeseries")
        timeseries = DemandTimeseries.objects.get(id=timeseries_id)

        if timeseries.units == "Wh":
            timeseries_values = timeseries.values
        elif timeseries.units == "kWh":
            timeseries_values = [value / 1000 for value in timeseries.values]
        else:
            return JsonResponse(
                {"error": "timeseries has unsupported unit"}, status=403
            )

        return JsonResponse({"timeseries_values": timeseries_values})

    return JsonResponse({"error": request})


def save_demand(request):
    # TODO save either aggregated demand profile to database or full demand data (with all consumer groups) when the
    #  user is finished
    return {"status": 200}


@json_view
@login_required
@require_http_methods(["GET", "POST"])
def upload_demand_timeseries(request):
    if request.method == "GET":
        n = DemandTimeseries.objects.count()
        form = UploadDemandForm(
            initial={
                "name": f"test_timeserie{n}",
                "ts_type": "source",
                "start_time": "2023-01-01",
                "end_time": "2023-01-31",
                "open_source": True,
                "units": "kWh",
            }
        )
        context = {"form": form}

        return render(request, "asset/upload_timeseries.html", context)

    elif request.method == "POST":
        qs = request.POST
        form = UploadDemandForm(qs)

        if form.is_valid():
            ts = form.save(commit=True)
            ts.user = request.user
