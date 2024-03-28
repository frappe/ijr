# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json

import frappe


def get_context(context):
    comparison_type = frappe.form_dict.type or ""
    selected_pillar = frappe.form_dict.pillar or "police"
    selected_indicators = frappe.form_dict.indicators or "123"
    selected_states = frappe.form_dict.states or "MH,UP"
    selected_ijrs = frappe.form_dict.ijrs or ""

    valid_comparison_types = [
        "indicator_by_ijr",
        "indicator_vs_indicator",
        "indicators_vs_states",
    ]
    if comparison_type not in valid_comparison_types:
        frappe.local.flags.redirect_location = f"/compare?type=indicator_by_ijr&pillar={selected_pillar}&indicators={selected_indicators}&states={selected_states}&ijrs={selected_ijrs}"
        raise frappe.Redirect

    if selected_indicators:
        if comparison_type == "indicator_by_ijr":
            selected_indicators = selected_indicators.split(",")[0]
        if comparison_type == "indicator_vs_indicator":
            selected_indicators = selected_indicators.split(",")[0:2]
            selected_indicators = ",".join(selected_indicators)

    data = []
    if selected_pillar and selected_indicators and selected_states:
        data = frappe.get_all(
            "State Indicator Data",
            filters={
                "pillar": frappe.unscrub(selected_pillar),
                "indicator_id": ["in", selected_indicators.split(",")],
                "region_code": ["in", selected_states.split(",")],
                "ijr_number": (
                    ["in", selected_ijrs.split(",")] if selected_ijrs else ["is", "set"]
                ),
            },
            fields=["state", "ijr_number", "indicator_id", "sum(indicator_value) as indicator_value"],
            order_by="ijr_number asc, state asc",
            group_by="state, ijr_number",
        )
        data = data

    select_options = prepare_select_options(frappe.form_dict)
    context.update(select_options)
    context.update(
        {
            "title": "Compare | India Justice Report",
            "comparison_type": comparison_type,
            "selected_pillar": selected_pillar,
            "selected_indicators": selected_indicators,
            "selected_states": selected_states,
            "selected_ijrs": selected_ijrs,
            "chart_title": "State-wise Indicator Comparison",
            "data": json.dumps(data),
        }
    )


def prepare_select_options(form_dict):
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

    indicator_options = [
        {"label": indicator.indicator_name, "value": indicator.name}
        for indicator in frappe.get_all(
            "State Indicator",
            fields=["name", "indicator_name"],
            filters={
                "pillar": (
                    frappe.unscrub(form_dict.get("pillar"))
                    if form_dict.get("pillar")
                    else ["is", "set"]
                )
            },
        )
    ]

    return {
        "ijr_options": ijr_options,
        "state_options": state_options,
        "pillar_options": pillar_options,
        "indicator_options": indicator_options,
    }
