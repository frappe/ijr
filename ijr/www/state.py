# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	state_code = frappe.form_dict.state
	pillar = frappe.form_dict.pillar or None
	theme = frappe.form_dict.theme or None

	ijr_number = 3
	state = frappe.get_doc('State', {'code': state_code})
	current_ranking = frappe.get_doc('State Ranking', {'region_code': state_code, 'ijr_number': ijr_number })

	all_rankings = frappe.db.get_all('State Ranking',
		filters={'region_code': state_code},
		fields=['*'],
		order_by='ijr_number desc'
	)

	total_rankings = frappe.db.get_all('State Ranking',
		filters={'cluster': current_ranking.cluster, 'ijr_number': ijr_number},
		fields=['count(name) as count'],
		pluck='count')[0]

	for d in all_rankings:
		d.ijr = f'IJR {d.ijr_number}'
		keys = ['overall', 'police', 'prisons', 'judiciary', 'legal_aid', 'hr', 'diversity', 'trends']
		for key in keys:
			color = get_value_color(d.get(f'{key}_rank'), total_rankings)
			d[f'{key}_rank_color'] = color
			d[f'{key}_score_color'] = color

	states = frappe.db.get_all('State', fields=['name', 'code', 'cluster'], order_by='cluster asc, name asc')
	states_by_cluster = {}
	for d in states:
		states_by_cluster.setdefault(d.cluster, []).append(d)

	# indicators data
	indicator_filters = {'region_code': state_code}
	if pillar:
		indicator_filters['pillar'] = pillar
	if theme:
		indicator_filters['theme'] = theme

	indicators_data = frappe.db.get_all('State Indicator Data',
		filters=indicator_filters,
		fields=['*']
	) if pillar or theme else []

	for row in indicators_data:
		row.ijr_score_color = ['', 'var(--best)', 'var(--middle)', 'var(--worst)'][row.color_code]

	context.raw_data = get_raw_data_by_indicator(state_code)
	context.state = state
	context.title = 'State Analysis: ' + context.state.name
	context.current_ranking = current_ranking
	context.total_rankings = total_rankings
	context.all_rankings = all_rankings
	context.states_by_cluster = states_by_cluster
	context.indicators_data = indicators_data

	context.active_tab = 'Overall'
	if pillar:
		context.active_tab = pillar
	elif theme:
		context.active_tab = theme

def get_value_color(value, max_value):
	one_third = frappe.utils.cint(max_value / 3)
	best_values = one_third
	middle_values = 2 * one_third

	if value <= best_values:
		return 'var(--best)'
	if value <= middle_values:
		return 'var(--middle)'
	return 'var(--worst)'

def get_raw_data_by_indicator(state_code):
	raw_data = frappe.db.get_all('State Indicator Raw Data',
		fields='*',
		filters={'region_code': state_code},
		order_by='raw_data_sequence asc, ijr_number asc'
	)
	raw_data_by_indicator = {}
	raw_data_with_all_ijrs = {}
	for r in raw_data:
		key = (r.indicator_id, r.raw_data_sequence)
		data = raw_data_by_indicator.get(key)
		if not data:
			data = raw_data_by_indicator[key] = r
		data[f'ijr_{r.ijr_number}_value'] = r.raw_data_value
		if r.ijr_number == 1:
			raw_data_with_all_ijrs.setdefault(r.indicator_id, []).append(data)
	return raw_data_with_all_ijrs