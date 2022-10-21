from math import floor

from django import template

register = template.Library()


@register.filter(name="beautiful_seconds")
def convert_seconds_to_intuitive_string(value):
    try:
        convert = lambda divisor, mod: floor(value / divisor % mod)
        days = convert(86400, 1)
        hours = convert(3600, 24)
        mins = convert(60, 60)
        secs = convert(1, 60)

        return f"{days}d {hours}h {mins}m {secs}s"

    except Exception as e:
        return str(e)


@register.filter(name="scenario_list")
def get_scenario_list_from_project(project):
    return project.scenario_set.all()


@register.filter
def pdb(element):
    import pdb

    pdb.set_trace()
    return element


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_field(form, key):
    return form.fields[key].get_bound_field(form, key)


@register.filter
def has_field(form, key):
    return key in form.fields


@register.filter
def has_economical_parameters(form):
    answer = False
    for field in form.fields:
        if is_economical_parameter(field):
            answer = True
            break
    return answer


@register.filter
def has_technical_parameters(form):
    answer = False
    for field in form.fields:
        if is_technical_parameter(field):
            answer = True
            break
    return answer


@register.filter
def is_economical_parameter(param):
    return param in [
        "capex_fix",
        "capex_var",
        "opex_fix",
        "opex_var",
        "energy_price",
        "feedin_tariff",
    ]


@register.filter
def is_technical_parameter(param):
    if param == "name":
        return False
    else:
        return not is_economical_parameter(param)


@register.filter
def get_selected_scenarios(request, proj_id):
    return request.session.get("selected_scenarios", {}).get(str(proj_id))
