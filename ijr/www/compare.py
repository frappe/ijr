# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json

import frappe

TABS = [
    "one_indicator",
    "two_indicator",
    "three_indicator",
]
DEFAULT_TAB = TABS[0]


def get_context(context):
    if frappe.form_dict.tab not in TABS:
        frappe.local.flags.redirect_location = f"/compare?tab={DEFAULT_TAB}"
        raise frappe.Redirect

    data = []
    data = frappe.get_all(
        "State Indicator Data",
        fields=[
            "indicator_id",
            "indicator_name",
            "state",
            "region_code",
            "cluster",
            "ijr_number",
            "year",
            "indicator_unit",
            "indicator_value",
            "pillar",
            "theme",
        ],
    )

    context.update(
        {
            "title": "Compare States | India Justice Report", 
            "data": json.dumps(data),
        }
    )


def sanitize_args(form_dict):
    tab = form_dict.tab
    if not tab or tab not in TABS:
        frappe.local.flags.redirect_location = f"/compare?tab={DEFAULT_TAB}"
        raise frappe.Redirect

    default_ijr = "all" if tab == "one_indicator" else "3"
    ijrs = form_dict.ijrs or default_ijr

    indicators = form_dict.indicators
    if indicators:
        if tab == "one_indicator":
            indicators = indicators.split(",")[0]
        if tab == "two_indicator":
            indicators = indicators.split(",")[0:2]
            indicators = ",".join(indicators)

    states = form_dict.states
    return frappe._dict(
        {
            "tab": tab,
            "indicators": indicators,
            "states": states,
            "ijrs": ijrs,
        }
    )


def validate_args(args):
    if args.tab == "one_indicator":
        return bool(args.indicators and args.states)
    if args.tab == "two_indicator":
        return bool(
            args.indicators and args.states and len(args.indicators.split(",")) >= 2
        )
    if args.tab == "multiple_indicator":
        return bool(args.indicators and args.states and len(args.states.split(",")) > 1)


def get_data_filters(args):
    state_filter = ["in", args.states.split(",")]
    indicator_filter = ["in", args.indicators.split(",")]
    ijr_filter = ["is", "set"]

    if args.ijrs and args.ijrs != "all":
        ijr_filter = ["in", args.ijrs.split(",")]

    if args.tab == "two_indicator":
        if args.states == "all":
            state_filter = ["is", "set"]
        if args.states == "large":
            state_filter = ["in", get_large_state_codes()]
        if args.states == "small":
            state_filter = ["in", get_small_state_codes()]

    return {
        "indicator_id": indicator_filter,
        "region_code": state_filter,
        "ijr_number": ijr_filter,
    }


def get_chart_title(form_dict):
    tab = form_dict.get("tab")
    selected_indicators = form_dict.get("indicators")

    chart_title = "<chart title>"
    if tab == "one_indicator":
        indicator_name = frappe.get_value(
            "State Indicator", selected_indicators, "indicator_name"
        )
        indicator_unit = frappe.db.get_value(
            "State Indicator Data",
            {"indicator_id": selected_indicators},
            "indicator_unit",
        )
        chart_title = f"{indicator_name} ({indicator_unit})"
    return chart_title


def get_select_options(form_dict):
    tab = form_dict.get("tab")
    ijr_options = [
        {"label": f"IJR {ijr_number}", "value": ijr_number}
        for ijr_number in frappe.get_all(
            "State Indicator Data",
            fields=["ijr_number"],
            order_by="ijr_number asc",
            distinct=True,
            pluck="ijr_number",
        )
    ]

    state_options = []
    if tab == "two_indicator":
        state_options = [
            {"label": "All states and UTs", "value": "all"},
            {"label": "18 large and mid-sized states", "value": "large"},
            {"label": "7 small states", "value": "small"},
        ]
    else:
        state_options = [
            {"label": state.name, "value": state.code}
            for state in frappe.get_all(
                "State",
                fields=["name", "code"],
                order_by="name asc",
            )
        ]

    indicator_options = [
        {
            "label": indicator.indicator_name,
            "value": indicator.name,
            "theme": indicator.theme,
            "pillar": indicator.pillar,
        }
        for indicator in frappe.get_all(
            "State Indicator",
            fields=["name", "indicator_name", "theme", "pillar"],
        )
    ]

    return {
        "ijr_options": ijr_options,
        "state_options": state_options,
        "indicator_options": frappe.as_json(indicator_options),
    }


def get_large_state_codes():
    return frappe.get_all(
        "State",
        filters={"cluster": "Large and mid-sized states"},
        pluck="code",
    )


def get_small_state_codes():
    return frappe.get_all(
        "State",
        filters={"cluster": "Small states"},
        pluck="code",
    )
