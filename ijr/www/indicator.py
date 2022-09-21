# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	view = frappe.form_dict.view or 'map'
	indicator_id = frappe.form_dict.indicator_id
	ijr_number = frappe.utils.cint(frappe.form_dict.ijr_number or '3')
	cluster = frappe.form_dict.cluster or 'large-mid'
	cluster_value = None
	if cluster == 'large-mid':
		cluster_value = 'Large / Mid State'
	if cluster == 'small':
		cluster_value = 'Small State'

	order_by = ''
	filters = {}
	if view == 'table':
		filters = {'indicator_id': indicator_id}
		order_by = 'state asc, ijr_number asc'
	elif view == 'map':
		filters = {'indicator_id': indicator_id, 'ijr_number': ijr_number, 'cluster': cluster_value}
		order_by = 'ijr_score desc'

	context.indicator_data = indicator_rankings_data(filters, order_by)
	if context.indicator_data:
		context.indicator_name = context.indicator_data[0].indicator_name

	if view == 'table':
		context.columns = [
			{
				'label': 'State',
				'id': 'state',
				'filter': True,
				'format': '''<a href="/state/${d.region_code}">${d.state}</a>'''
			},
			{'label': 'IJR', 'id': 'ijr_number', 'align': 'center', 'filter': True},
			{'label': 'Year', 'id': 'year'},
			{'label': 'Score', 'id': 'ijr_score', 'format': '''return Number(d.ijr_score).toFixed(2)''', 'align': 'right'},
			{'label': 'Indicator Value', 'id': 'indicator_value'},
			{'label': 'Indicator Unit', 'id': 'indicator_unit'},
		]
		if context.indicator_data:
			for d in context.indicator_data[0].raw_data:
				context.columns.append({
					'label': d.raw_data_name,
					'id': d.raw_data_name,
				})
			for row in context.indicator_data:
				for d in row.raw_data:
					row[d.raw_data_name] = f'{d.raw_data_value} {d.raw_data_unit}'

	context.raw_data = get_raw_data_by_state(indicator_id)
	context.indicator_id = indicator_id
	context.indicators = frappe.db.get_all('State Indicator', fields=['distinct(`indicator_id`) as value', 'indicator_name as label'], order_by='indicator_name asc')
	context.view = view
	context.ijr_number = ijr_number
	context.cluster = cluster
	context.no_cache = 1


def indicator_rankings_data(filters, order_by):
	data = frappe.get_all('State Indicator',
		filters=filters,
		fields=['*'],
		order_by=order_by
	)

	# prev ijr data for comparison
	prev_ijr_data_by_state = {}
	if filters.get('ijr_number'):
		prev_ijr_filters = filters.copy().update({'ijr_number': filters.get('ijr_number') - 1})
		prev_ijr_data = frappe.get_all('State Indicator',
			filters=prev_ijr_filters,
			fields=['*'],
			order_by=order_by
		)
		for d in prev_ijr_data:
			prev_ijr_data_by_state[d.state] = d

	for d in data:
		d.ijr_score_color = ['', 'var(--best)', 'var(--middle)', 'var(--worst)'][d.color_code or 0]
		# delta
		d.ijr_score_delta = d.ijr_score - prev_ijr_data_by_state.get(d.state, {}).get('ijr_score', 0)
		d.raw_data = frappe.db.get_all('State Indicator Raw Data',
			filters={'ijr_number': d.ijr_number, 'state': d.state, 'indicator_id': d.indicator_id},
			fields=['*'],
			order_by='raw_data_sequence asc'
		)

	return data

def get_raw_data_by_state(indicator_id):
	raw_data = frappe.db.get_all('State Indicator Raw Data',
		fields='*',
		filters={'indicator_id': indicator_id},
		order_by='raw_data_sequence asc, ijr_number asc'
	)
	raw_data_by_state = {}
	raw_data_with_all_ijrs = {}
	for r in raw_data:
		key = (r.state, r.raw_data_sequence)
		data = raw_data_by_state.get(key)
		if not data:
			data = raw_data_by_state[key] = r
		data[f'ijr_{r.ijr_number}_value'] = r.raw_data_value
		if r.ijr_number == 1:
			raw_data_with_all_ijrs.setdefault(r.state, []).append(data)
	return raw_data_with_all_ijrs