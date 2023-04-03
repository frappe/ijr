# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from ijr.jinja_helpers import rankings_url


def get_context(context):
	if not frappe.form_dict:
		url = rankings_url(defaults_only=True)
		frappe.local.flags.redirect_location = url
		raise frappe.Redirect

	view = frappe.form_dict.view or 'map'
	rank_by = frappe.form_dict.rank_by or 'overall'
	default_ijr = 3 if view == 'map' else 0
	ijr_number = cint(frappe.form_dict.ijr_number or default_ijr)

	if view == 'map' and ijr_number == 0:
		ijr_number = 3

	cluster = frappe.form_dict.cluster or 'large-states'

	state_rankings = state_rankings_data(ijr_number=ijr_number, cluster=cluster, rank_by=rank_by)

	title = 'Overall State Rankings'
	rank_by_title = 'Overall'
	description = 'Performance across police, prisons, judiciary and legal aid'
	_pillar = None
	_theme = None
	table_view = 'pillars'
	if rank_by != 'overall':
		if _pillar := get_pillar(rank_by):
			rank_by_title = _pillar.name
			description = _pillar.description
			title = f'State Rankings by {_pillar.name}'
			table_view = 'pillars'
		elif _theme := get_theme(rank_by):
			rank_by_title = _theme.name
			description = _theme.description
			title = f'State Rankings by {_theme.name}'
			table_view = 'themes'

	context.title = f'{title} | India Justice Report'
	context.description = description
	context.image = frappe.db.get_single_value('IJR Settings', 'rankings_meta_image')
	context.rank_by_title = rank_by_title
	context.state_rankings = state_rankings
	context.view = view
	context.cluster = cluster
	context.table_view = table_view
	context.rank_by = rank_by
	context.ijr_number = ijr_number
	context.form_dict = frappe.form_dict

	help_text = ''
	if cluster == 'large-states' and view == 'map':
		help_text = '''The visualisation shows the performance of the cluster of 18 large and mid-sized states
		(population above 10 million) in IJR 2022. States ranked 1-6 are shown in dark green, those ranked 7-
		12 in light green and those ranked 13-18 in light brown. The mouseover on the map shows,
		additionally, each state’s rank across 4 pillars and 3 ranked themes. Use the dropdown on top
		left to see performance in IJR 2019 and IJR 2020.'''
	elif cluster == 'small-states' and view == 'map':
		help_text = '''The visualisation shows the performance of the cluster of 7 small states (population below 10
		million) in IJR 2022. States ranked 1-3 are shown in dark green, those ranked 4-5 in light green and
		those ranked 6-7 in light brown. The mouseover on the map shows, additionally, each state’s
		rank across 4 pillars and 3 ranked themes. Use the dropdown on top left to see performance in
		IJR 2019 and IJR 2020.'''
	elif cluster == 'large-states' and view == 'table':
		help_text = '''The visualisation shows the performance of the cluster of 18 large and mid-sized states
		(population above 10 million) across all three IJRs. Besides an overall ranking, states are ranked
		by 4 pillars and 3 ranked themes. States ranked 1-6 are shown in dark green, those ranked 7-12 in
		light green and those ranked 13-18 in light brown. The column header has sort and filter
		features. Use the sort feature to sort any column in ascending or descending order. Use the
		filter feature in the first two columns to compare states or see results for only one IJR.'''
	elif cluster == 'small-states' and view == 'table':
		help_text = '''The visualisation shows the performance of the cluster of 7 small states (population below 10
		million) across all three IJRs. Besides an overall ranking, states are ranked by 4 pillars and 3
		ranked themes. States ranked 1-3 are shown in dark green, those ranked 4-5 in light green and those
		ranked 6-7 in light brown. The column header has sort and filter features. Use the sort feature
		to sort any column in ascending or descending order. Use the filter feature in the first two
		columns to compare states or see results for only one IJR.'''

	context.help_text = help_text




def state_rankings_data(ijr_number, cluster, rank_by):
	if cluster == 'large-states':
		cluster = 'Large and mid-sized states'
	if cluster == 'small-states':
		cluster = 'Small states'

	filters = {'cluster': cluster}
	if ijr_number:
		filters['ijr_number'] = ijr_number

	order_by = f'{rank_by}_rank asc'
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
		prev_ijr_filters = filters.copy()
		prev_ijr_filters.update({'ijr_number': prev_ijr_number})
		prev_ijr_data = frappe.get_all('State Ranking',
			filters=prev_ijr_filters,
			fields=['*'],
			order_by=f'{rank_by}_rank asc'
		)
		prev_ijr_data_by_state = {}
		for d in prev_ijr_data:
			prev_ijr_data_by_state[d.state] = d

	for d in data:
		for k in ['overall', 'police', 'prisons', 'judiciary', 'legal_aid', 'hr', 'diversity', 'trends']:
			color_code = d[f'{k}_color']
			d[f'{k}_rank_color'] = get_color(color_code)

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

	return data

def get_pillar(slug=None):
	if not slug: return
	return frappe.db.get_value('Pillar', {'slug': slug}, '*', as_dict=True)

def get_theme(slug=None):
	if not slug: return
	return frappe.db.get_value('Theme', {'slug': slug}, '*', as_dict=True)

def get_color(color_code):
	color_code = cint(color_code)
	color_map = {
		1: 'var(--best)',
		2: 'var(--middle)',
		3: 'var(--worst)'
	}
	return color_map.get(color_code) or 'var(--sl-color-gray-100)'
