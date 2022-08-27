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
		d.overall_rank_color = get_value_color(d.overall_rank, total_rankings)
		d.police_rank_color = get_value_color(d.police_rank, total_rankings)
		d.prisons_rank_color = get_value_color(d.prisons_rank, total_rankings)
		d.judiciary_rank_color = get_value_color(d.judiciary_rank, total_rankings)
		d.legal_aid_rank_color = get_value_color(d.legal_aid_rank, total_rankings)
		d.hr_rank_color = get_value_color(d.hr_rank, total_rankings)
		d.diversity_rank_color = get_value_color(d.diversity_rank, total_rankings)
		d.trends_rank_color = get_value_color(d.trends_rank, total_rankings)

	states = frappe.db.get_all('State', fields=['name', 'code', 'type'], order_by='type asc, name asc')
	states_by_cluster = {}
	for d in states:
		states_by_cluster.setdefault(d.type, []).append(d)

	# indicators data
	indicator_filters = {'region_code': state_code}
	if pillar:
		indicator_filters['pillar'] = pillar
	if theme:
		indicator_filters['theme'] = theme

	indicators_data = frappe.db.get_all('State Indicator',
		filters=indicator_filters,
		fields=['*']
	) if pillar or theme else []

	for row in indicators_data:
		row.raw_data = frappe.db.get_all('State Indicator Raw Data',
			fields='*',
			filters={
				'ijr_number': row.ijr_number,
				'indicator_id': row.indicator_id,
				'state': row.state
			},
			order_by='raw_data_sequence asc'
		)

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
