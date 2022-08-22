# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	view = frappe.form_dict.view or 'map'
	indicator_id = frappe.form_dict.indicator_id
	ijr_number = frappe.form_dict.ijr_number or '3'
	cluster = frappe.form_dict.cluster or 'Large / Mid State'

	if view == 'table':
		context.indicator_data = frappe.db.get_all(
			'State Indicator',
			filters={'indicator_id': indicator_id},
			fields=['*'],
			order_by='state asc, ijr_number asc'
		)
	elif view == 'map':
		context.indicator_data = indicator_rankings_data(indicator_id=indicator_id, ijr_number=ijr_number, cluster=cluster)

	if context.indicator_data:
		context.indicator_name = context.indicator_data[0].indicator_name

	context.indicator_id = indicator_id
	context.indicators = frappe.db.get_all('State Indicator', fields=['distinct(`indicator_id`) as value', 'indicator_name as label'], order_by='indicator_name asc')
	context.view = view


def indicator_rankings_data(indicator_id, ijr_number, cluster):
	ijr_number = frappe.utils.cint(ijr_number)

	if cluster == 'large-mid':
		cluster = 'Large / Mid State'
	if cluster == 'small':
		cluster = 'Small State'

	filters = {'indicator_id': indicator_id, 'ijr_number': ijr_number, 'cluster': cluster}

	data = frappe.get_all('State Indicator',
		filters=filters,
		fields=['*'],
		order_by='ijr_score desc'
	)

	# prev ijr data for comparison
	prev_ijr_filters = filters.copy().update({'ijr_number': ijr_number - 1})
	prev_ijr_data = frappe.get_all('State Indicator',
		filters=prev_ijr_filters,
		fields=['*'],
		order_by=f'ijr_score desc'
	)
	prev_ijr_data_by_state = {}
	for d in prev_ijr_data:
		prev_ijr_data_by_state[d.state] = d

	colors = ["var(--best)",  "var(--middle)", "var(--worst)"]

	for d in data:
		d.color = colors[d.color_code - 1] if d.color_code else None
		# delta
		d.ijr_score_delta = d.ijr_score - prev_ijr_data_by_state.get(d.state, {}).ijr_score
		d.raw_data = frappe.db.get_all('State Indicator Raw Data',
			filters={'ijr_number': d.ijr_number, 'state': d.state, 'indicator_id': d.indicator_id},
			fields=['*'],
			order_by='raw_data_sequence asc'
		)

	return data

