# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	view = frappe.form_dict.view or 'map'
	table_view = frappe.form_dict.table_view or 'pillars'
	rank_by = frappe.form_dict.rank_by or 'overall'
	ijr_number = frappe.form_dict.ijr_number or '3'

	cluster = frappe.form_dict.cluster or 'large-mid'
	cluster_filter = None
	if cluster == 'large-mid':
		cluster_filter = 'Large / Mid State'
	if cluster == 'small':
		cluster_filter = 'Small State'

	state_rankings = state_rankings_data(ijr_number=ijr_number, cluster=cluster_filter, rank_by=rank_by)

	title = 'IJR Insights'
	if view == 'table':
		title = title + f' | {table_view.title()} Table View'
	if view == 'map':
		title = title + ' | Overall Ranking | Map View'

	context.title = title
	context.state_rankings = state_rankings
	context.view = view
	context.cluster = cluster
	context.table_view = table_view
	context.rank_by = rank_by
	context.ijr_number = ijr_number
	context.form_dict = frappe.form_dict





def state_rankings_data(ijr_number, cluster, rank_by):
	ijr_number = frappe.utils.cint(ijr_number)

	if cluster == 'large-mid':
		cluster = 'Large / Mid State'
	if cluster == 'small':
		cluster = 'Small State'

	filters = {'ijr_number': ijr_number, 'cluster': cluster}

	data = frappe.get_all('State Ranking',
		filters=filters,
		fields=['*'],
		order_by=f'{rank_by}_score desc'
	)

	# prev ijr data for comparison
	prev_ijr_filters = filters.copy().update({'ijr_number': ijr_number - 1})
	prev_ijr_data = frappe.get_all('State Ranking',
		filters=prev_ijr_filters,
		fields=['*'],
		order_by=f'{rank_by}_score desc'
	)
	prev_ijr_data_by_state = {}
	for d in prev_ijr_data:
		prev_ijr_data_by_state[d.state] = d


	colors = ["var(--best)",  "var(--middle)", "var(--worst)"]
	legend = ['Best', 'Middle', 'Worst']

	third = frappe.utils.cint(len(data) / 3)

	def get_value_type(value, max_value):
		one_third = frappe.utils.cint(max_value / 3)
		best_values = one_third
		middle_values = 2 * one_third

		if value <= best_values:
			return 'var(--best)'
		if value <= middle_values:
			return 'var(--middle)'
		return 'var(--worst)'

	i = 0
	for d in data:
		d.overall_rank_color = get_value_type(d.overall_rank, len(data))
		d.police_rank_color = get_value_type(d.police_rank, len(data))
		d.prisons_rank_color = get_value_type(d.prisons_rank, len(data))
		d.judiciary_rank_color = get_value_type(d.judiciary_rank, len(data))
		d.legal_aid_rank_color = get_value_type(d.legal_aid_rank, len(data))
		d.hr_rank_color = get_value_type(d.hr_rank, len(data))
		d.diversity_rank_color = get_value_type(d.diversity_rank, len(data))
		d.trends_rank_color = get_value_type(d.trends_rank, len(data))

		# delta
		d.overall_rank_delta = d.overall_rank - prev_ijr_data_by_state[d.state].overall_rank
		d.police_rank_delta = d.police_rank - prev_ijr_data_by_state[d.state].police_rank
		d.prisons_rank_delta = d.prisons_rank - prev_ijr_data_by_state[d.state].prisons_rank
		d.judiciary_rank_delta = d.judiciary_rank - prev_ijr_data_by_state[d.state].judiciary_rank
		d.legal_aid_rank_delta = d.legal_aid_rank - prev_ijr_data_by_state[d.state].legal_aid_rank
		d.hr_rank_delta = d.hr_rank - prev_ijr_data_by_state[d.state].hr_rank
		d.diversity_rank_delta = d.diversity_rank - prev_ijr_data_by_state[d.state].diversity_rank
		d.trends_rank_delta = d.trends_rank - prev_ijr_data_by_state[d.state].trends_rank

		i = i + 1

	return data



