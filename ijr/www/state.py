# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from ijr.www.rankings import get_color, get_pillar, get_theme
from frappe.utils import cint
from frappe.utils.formatters import format_value


def get_context(context):
	state_code = frappe.form_dict.state
	pillar = frappe.form_dict.pillar or None
	theme = frappe.form_dict.theme or None
	ijr_number = cint(frappe.form_dict.ijr_number or 3)

	_pillar = get_pillar(pillar)
	_theme = get_theme(theme)
	description = 'Performance across police, prisons, judiciary and legal aid'
	if _pillar:
		pillar = _pillar.name
		description = _pillar.description
	elif _theme:
		theme = _theme.name
		description = _theme.description

	state = frappe.get_doc('State', {'code': state_code})
	current_ranking = None
	previous_ranking = None
	if frappe.db.exists('State Ranking', {'region_code': state_code, 'ijr_number': ijr_number }):
		current_ranking = frappe.get_doc('State Ranking', {'region_code': state_code, 'ijr_number': ijr_number })
		previous_ijr_number = ijr_number - 1
		if frappe.db.exists('State Ranking', {'region_code': state_code, 'ijr_number': previous_ijr_number }):
			previous_ranking = frappe.get_doc('State Ranking', {'region_code': state_code, 'ijr_number': previous_ijr_number })

	all_rankings = frappe.db.get_all('State Ranking',
		filters={'region_code': state_code},
		fields=['*'],
		order_by='ijr_number desc'
	)

	for d in all_rankings:
		d.ijr = f'IJR {d.ijr_number}'
		keys = ['overall', 'police', 'prisons', 'judiciary', 'legal_aid', 'hr', 'diversity', 'trends']
		for key in keys:
			color = get_color(d.get(f'{key}_color'))
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
		fields=['*'],
		order_by='ijr_number desc, indicator_name asc'
	) if pillar or theme else []

	for row in indicators_data:
		row.ijr_score_color = ['', 'var(--best)', 'var(--middle)', 'var(--worst)'][row.color_code]
		row.indicator_value_formatted = format_value(row.indicator_value, {
			'fieldtype': 'Float',
			'precision': row.indicator_value_decimals or None
		})
		row.ijr_score_formatted = format_value(row.ijr_score, {
			'fieldtype': 'Float',
			'precision': row.ijr_score_decimals or None
		})

	context.raw_data = get_raw_data_by_indicator(state_code)
	context.state = state
	context.title = f'{context.state.name} State Analysis | India Justice Report'
	context.description = description
	context.current_ranking = current_ranking
	context.previous_ranking = previous_ranking
	context.all_rankings = all_rankings
	context.indicators_data = indicators_data
	context.ijr_number = ijr_number

	context.active_tab = 'Overall'
	if pillar:
		context.active_tab = pillar
	elif theme:
		context.active_tab = theme

	active_tab_field = _pillar.slug if _pillar else _theme.slug if _theme else 'overall'
	context.active_tab_field = active_tab_field
	context.active_tab_rank = current_ranking.get(f'{active_tab_field}_rank') if current_ranking else None
	context.active_tab_score = current_ranking.get(f'{active_tab_field}_score') if current_ranking else None
	context.active_tab_color = current_ranking.get(f'{active_tab_field}_color') if current_ranking else None
	if current_ranking and previous_ranking:
		context.active_tab_score_delta = current_ranking.get(f'{active_tab_field}_score') - previous_ranking.get(f'{active_tab_field}_score')
		context.active_tab_score_delta = round(context.active_tab_score_delta, 2)
		context.active_tab_rank_delta = current_ranking.get(f'{active_tab_field}_rank') - previous_ranking.get(f'{active_tab_field}_rank')

def get_raw_data_by_indicator(state_code):
	raw_data = frappe.db.get_all('State Indicator Raw Data',
		fields='*',
		filters={'region_code': state_code},
		order_by='raw_data_sequence asc, ijr_number asc, year asc'
	)
	raw_data_by_indicator = {}
	raw_data_with_all_ijrs = {}
	for r in raw_data:
		if r.theme == 'Trends':
			key = (r.indicator_id, r.ijr_number, r.year, r.raw_data_sequence)
			data = raw_data_by_indicator.get(key)
			if not data:
				data = raw_data_by_indicator[key] = r

			_key = f'{r.indicator_id}-{r.ijr_number}'
			raw_data_with_all_ijrs.setdefault(_key, []).append(data)
		else:
			key = (r.indicator_id, r.raw_data_sequence)
			data = raw_data_by_indicator.get(key)
			if not data:
				data = raw_data_by_indicator[key] = r
			raw_data_value = format_value(r.raw_data_value, {
				'fieldtype': 'Float',
				'precision': r.raw_data_value_decimals or None
			})
			data[f'ijr_{r.ijr_number}_value'] = raw_data_value
			if r.ijr_number == 1:
				raw_data_with_all_ijrs.setdefault(r.indicator_id, []).append(data)
	return raw_data_with_all_ijrs
