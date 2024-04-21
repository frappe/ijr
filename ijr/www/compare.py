# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json

import frappe


def get_context(context):
    comparison_type = frappe.form_dict.type or ""
    selected_pillars = frappe.form_dict.pillars or ""
    selected_indicators = frappe.form_dict.indicators or ""
    selected_states = frappe.form_dict.states or ""
    selected_ijrs = frappe.form_dict.ijrs or (
        "*" if comparison_type == "one_indicator" else "3"
    )

    valid_comparison_types = [
        "one_indicator",
        "two_indicator",
        "multiple_indicator",
    ]
    if comparison_type not in valid_comparison_types:
        frappe.local.flags.redirect_location = f"/compare?type=one_indicator&pillars={selected_pillars}&indicators={selected_indicators}&states={selected_states}&ijrs={selected_ijrs}"
        raise frappe.Redirect

    if selected_indicators:
        if comparison_type == "one_indicator":
            selected_indicators = selected_indicators.split(",")[0]
        if comparison_type == "two_indicator":
            selected_indicators = selected_indicators.split(",")[0:2]
            selected_indicators = ",".join(selected_indicators)

    data = []
    if validate_filters(
        comparison_type,
        selected_pillars,
        selected_indicators,
        selected_states,
        selected_ijrs,
    ):
        state_filter = ["in", selected_states.split(",")]
        if comparison_type == "two_indicator":
            if selected_states == "all":
                state_filter = ["is", "set"]
            if selected_states == "large":
                state_filter = ["in", ["MH", "TN", "GJ", "KA", "AP", "RJ", "MP"]]
            if selected_states == "small":
                state_filter = [
                    "in",
                    [
                        "TR",
                        "ML",
                        "NL",
                        "MZ",
                        "SK",
                        "AR",
                        "GA",
                    ],
                ]
        data = frappe.get_all(
            "State Indicator Data",
            filters={
                "pillar": [
                    "in",
                    [frappe.unscrub(p) for p in selected_pillars.split(",")],
                ],
                "indicator_id": ["in", selected_indicators.split(",")],
                "region_code": state_filter,
                "ijr_number": (
                    ["in", selected_ijrs.split(",")]
                    if selected_ijrs and selected_ijrs != "*"
                    else ["is", "set"]
                ),
            },
            fields=[
                "state",
                "ijr_number",
                "indicator_id",
                "indicator_name",
                "indicator_unit",
                "sum(indicator_value) as indicator_value",
            ],
            order_by="ijr_number asc, state asc",
            group_by="state, ijr_number, indicator_id",
        )
        data = data

    chart_title = get_chart_title(frappe.form_dict)
    select_options = prepare_select_options(frappe.form_dict)
    context.update(select_options)
    context.update(
        {
            "title": "Compare | India Justice Report",
            "comparison_type": comparison_type,
            "selected_pillar": selected_pillars,
            "selected_indicators": selected_indicators,
            "selected_states": selected_states,
            "selected_ijrs": selected_ijrs,
            "chart_title": chart_title,
            "data": json.dumps(data),
        }
    )


def validate_filters(comparison_type, pillar, indicators, states, ijrs):
    if comparison_type == "one_indicator":
        return bool(pillar and indicators and states)
    if comparison_type == "two_indicator":
        return bool(
            pillar and indicators and states and len(indicators.split(",")) >= 2
        )
    if comparison_type == "multiple_indicator":
        return bool(
            pillar
            and indicators
            and states
            and len(indicators.split(",")) > 1
            and len(states.split(",")) > 1
        )


def get_chart_title(form_dict):
    comparison_type = form_dict.get("type")
    selected_indicators = form_dict.get("indicators")

    chart_title = "<chart title>"
    if comparison_type == "one_indicator":
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


def prepare_select_options(form_dict):
    comparison_type = form_dict.get("type")
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
    if comparison_type == "two_indicator":
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

    pillar_options = [
        {"label": pillar.name, "value": pillar.slug}
        for pillar in frappe.get_all(
            "Pillar",
            fields=["name", "slug"],
            order_by="name asc",
        )
    ]

    pillar_filter = ["is", "set"]
    if form_dict.get("pillars"):
        pillar_filter = [
            "in",
            [frappe.unscrub(p) for p in form_dict.get("pillars").split(",")],
        ]
    indicator_options = [
        {"label": indicator.indicator_name, "value": indicator.name}
        for indicator in frappe.get_all(
            "State Indicator",
            fields=["name", "indicator_name"],
            filters={
                "pillar": pillar_filter,
                "theme": (
                    ["!=", "Trends"]
                    if comparison_type == "one_indicator"
                    else ["is", "set"]
                ),
            },
        )
    ]

    return {
        "ijr_options": ijr_options,
        "state_options": state_options,
        "pillar_options": pillar_options,
        "indicator_options": indicator_options,
    }
