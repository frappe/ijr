# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	state_code = frappe.form_dict.state
	ijr_number = 3
	context.state = frappe.get_doc('State', {'code': state_code})
	current_ranking = frappe.get_doc('State Ranking', {'region_code': state_code, 'ijr_number': ijr_number })


	total_rankings = frappe.db.get_all('State Ranking',
		filters={'cluster': current_ranking.cluster, 'ijr_number': ijr_number},
		fields=['count(name) as count'],
		pluck='count')[0]


	all_rankings = frappe.db.get_all('State Ranking',
		filters={'region_code': state_code},
		fields=['*'],
		order_by='ijr_number asc'
	)

	colors = ["var(--best)",  "var(--middle)", "var(--worst)"]

	def get_value_type(value, max_value):
		one_third = frappe.utils.cint(max_value / 3)
		best_values = one_third
		middle_values = 2 * one_third

		if value <= best_values:
			return 'Best'
		if value <= middle_values:
			return 'Middle'
		return 'Worst'

	ranking_by_ijr = {}

	for d in all_rankings:
		d.ijr = f'IJR {d.ijr_number}'
		d.overall_rank_type = get_value_type(d.overall_rank, total_rankings)
		d.police_rank_type = get_value_type(d.police_rank, total_rankings)
		d.prisons_rank_type = get_value_type(d.prisons_rank, total_rankings)
		d.judiciary_rank_type = get_value_type(d.judiciary_rank, total_rankings)
		d.legal_aid_rank_type = get_value_type(d.legal_aid_rank, total_rankings)
		d.hr_rank_type = get_value_type(d.hr_rank, total_rankings)
		d.diversity_rank_type = get_value_type(d.diversity_rank, total_rankings)
		d.trends_rank_type = get_value_type(d.trends_rank, total_rankings)

		ranking_by_ijr[d.ijr_number] = d

	state_performance_data = []
	dimensions = [
		{'label': 'Overall', 'key': 'overall_rank'},
		{'label': 'Police', 'key': 'police_rank'},
		{'label': 'Prisons', 'key': 'prisons_rank'},
		{'label': 'Judiciary', 'key': 'judiciary_rank'},
		{'label': 'Legal Aid', 'key': 'legal_aid_rank'},
		{'label': 'HR', 'key': 'hr_rank'},
		{'label': 'Diversity', 'key': 'diversity_rank'},
		{'label': 'Trends', 'key': 'trends_rank'},
	]

	for d in dimensions:
		item = {
			'dimension': d['label'],
			'key': d['key']
		}
		for n in [1, 2, 3]:
			value = ranking_by_ijr[n][d['key']]
			item[f'ijr_{n}'] = value
			item[f'ijr_{n}_type'] = get_value_type(value, total_rankings)

		state_performance_data.append(item)


	states = frappe.db.get_all('State', fields=['name', 'code', 'type'], order_by='type asc, name asc')

	states_by_cluster = {}
	for d in states:
		states_by_cluster.setdefault(d.type, []).append(d)

	# indicators
	pillar = frappe.form_dict.pillar or None
	theme = frappe.form_dict.theme or None

	indicator_filters = {'region_code': state_code}
	if pillar:
		indicator_filters['pillar'] = pillar
	if theme:
		indicator_filters['theme'] = theme

	context.indicators_data = frappe.db.get_all('State Indicator',
		filters=indicator_filters,
		fields=['*']
	) if pillar or theme else []

	for row in context.indicators_data:
		row.raw_data = frappe.db.get_all('State Indicator Raw Data',
			fields='*',
			filters={
				'ijr_number': row.ijr_number,
				'indicator_id': row.indicator_id,
				'state': row.state
			},
			order_by='raw_data_sequence asc'
		)

	context.indicators_columns = [
		{'name': 'Indicator', 'id': 'indicator_name'},
		{'name': 'IJR Number', 'id': 'ijr_number'},
		{'name': 'Year', 'id': 'year'},
		{'name': 'Score', 'id': 'ijr_score'},
		{'name': 'Indicator Value', 'id': 'indicator_value'},
		{'name': 'Indicator Unit', 'id': 'indicator_unit'},
		{'name': 'Calculation', 'id': 'indicator_name'},
	]


	context.title = 'State Analysis: ' + context.state.name
	context.current_ranking = current_ranking
	context.total_rankings = total_rankings
	context.all_rankings = all_rankings
	context.ranking_by_ijr = ranking_by_ijr
	context.state_performance_data = state_performance_data
	context.states = states
	context.states_by_cluster = states_by_cluster
	context.colors = colors

