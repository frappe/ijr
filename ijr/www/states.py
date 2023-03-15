# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	view = frappe.form_dict.view or 'map'
	table_view = frappe.form_dict.table_view or 'pillars'
	rank_by = frappe.form_dict.rank_by or 'overall'
	ijr_number = frappe.form_dict.ijr_number or '3'

	if view == 'map' and ijr_number in ['0', 0]:
		ijr_number = 3

	cluster = frappe.form_dict.cluster or 'large-mid'
	cluster_filter = None
	if cluster == 'large-mid':
		cluster_filter = 'Large and mid-sized states'
	if cluster == 'small':
		cluster_filter = 'Small states'

	state_rankings = state_rankings_data(ijr_number=ijr_number, cluster=cluster_filter, rank_by=rank_by)

	title = 'IJR Insights'
	if view == 'table':
		title = title + f' | {table_view.title()} Table View'
	if view == 'map':
		title = title + ' | Overall Ranking | Map View'

	rank_by_title = 'Overall'
	description = 'Performance across police, prisons, judiciary and legal aid'
	if rank_by != 'overall':
		if _pillar := get_pillar(rank_by):
			rank_by_title = _pillar.name
			description = _pillar.description
		elif _theme := get_theme(rank_by):
			rank_by_title = _theme.name
			description = _theme.description

	context.title = title
	context.description = description
	context.rank_by_title = rank_by_title
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
		cluster = 'Large and mid-sized states'
	if cluster == 'small':
		cluster = 'Small states'

	filters = {'cluster': cluster}
	if ijr_number:
		filters['ijr_number'] = ijr_number

	order_by = f'{rank_by}_score desc'
	if ijr_number == 0:
		order_by = 'state asc, ijr_number asc'

	data = frappe.get_all('State Ranking',
		filters=filters,
		fields=['*'],
		order_by=order_by
	)

	# prev ijr data for comparison
	prev_ijr_number = ijr_number - 1 if ijr_number > 1 else None

	if prev_ijr_number:
		prev_ijr_filters = filters.copy().update({'ijr_number': prev_ijr_number})
		prev_ijr_data = frappe.get_all('State Ranking',
			filters=prev_ijr_filters,
			fields=['*'],
			order_by=f'{rank_by}_score desc'
		)
		prev_ijr_data_by_state = {}
		for d in prev_ijr_data:
			prev_ijr_data_by_state[d.state] = d

	color_map = {
		1: 'var(--best)',
		2: 'var(--middle)',
		3: 'var(--worst)'
	}

	i = 0
	for d in data:
		for k in ['overall', 'police', 'prisons', 'judiciary', 'legal_aid', 'hr', 'diversity', 'trends']:
			color_code = d[f'{k}_color']
			d[f'{k}_rank_color'] = color_map.get(color_code) or 'var(--brand-color)'

		if prev_ijr_number:
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

def get_pillar(slug=None):
	if not slug: return
	return frappe.db.get_value('Pillar', {'slug': slug}, '*', as_dict=True)

def get_theme(slug=None):
	if not slug: return
	return frappe.db.get_value('Theme', {'slug': slug}, '*', as_dict=True)
