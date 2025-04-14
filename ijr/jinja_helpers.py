# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint

def get_states_by_cluster():
	states = frappe.db.get_all('State', fields=['name', 'code', 'cluster'], order_by='cluster asc, name asc')
	states_by_cluster = {}
	for d in states:
		states_by_cluster.setdefault(d.cluster, []).append(d)
	return states_by_cluster

def get_indicators_by_pillars_and_themes():
	indicators = frappe.db.get_all('State Indicator',
		fields=['`name` as value', '`indicator_name` as label', 'pillar', 'theme', 'badge'],
		order_by='name asc'
	)
	indicators_by_pillars_and_themes = {}
	for i in indicators:
		indicators_by_pillars_and_themes.setdefault(i.pillar, {}).setdefault(i.theme, []).append(i)
	return indicators_by_pillars_and_themes

def get_ijr_options():
	ijr_numbers = frappe.db.get_all('IJR Number', fields=['*'], order_by='name asc')
	return [{'label': f'{i.title} ({i.year})', 'value': cint(i.name)} for i in ijr_numbers]


def get_color(color_code):
	color_code = cint(color_code)
	color_map = {
		1: 'var(--best)',
		2: 'var(--middle)',
		3: 'var(--worst)'
	}
	return color_map.get(color_code)

def get_key_color(d, key):
	return get_color(d.get(key + '_color'))

def get_current_url():
	return frappe.local.request.url

def rankings_url(**kwargs):
	'''
	Returns the rankings url based on the given values and fills in default values.
	/rankings/ijr-<ijr_number>/<rank_by>/<cluster>/<view>
	'''
	pillar_slugs = frappe.db.get_all('Pillar', pluck='slug')
	theme_slugs = frappe.db.get_all('Theme', pluck='slug')
	default_ijr_number = frappe.db.get_single_value('IJR Settings', 'default_ijr')
	ijr_numbers = ['0'] + frappe.db.get_all('IJR Number', pluck='name', order_by='name asc')
	ijr_numbers = [cint(i) for i in ijr_numbers]

	meta = {
		'ijr_number': { 'default': default_ijr_number, 'values': ijr_numbers },
		'cluster': { 'default': 'large-states', 'values': ['large-states', 'small-states'] },
		'rank_by': { 'default': 'overall', 'values': ['overall'] + pillar_slugs + theme_slugs },
		'view': { 'default': 'map', 'values': ['map', 'table'] }
	}

	kwargs = _validate_parameters(kwargs, meta)
	return '/rankings/ijr-{ijr_number}/{rank_by}/{cluster}/{view}'.format(**kwargs)

def state_url(**kwargs):
	'''
	Returns the state url based on the given values and fills in default values.
	/state/<state>/ijr-<ijr_number>/<pillar_or_theme>
	'''
	pillar_slugs = frappe.db.get_all('Pillar', pluck='slug')
	theme_slugs = frappe.db.get_all('Theme', pluck='slug')
	state_codes = frappe.db.get_all('State', pluck='code')
	default_ijr_number = frappe.db.get_single_value('IJR Settings', 'default_ijr')
	ijr_numbers = ['0'] + frappe.db.get_all('IJR Number', pluck='name', order_by='name asc')
	ijr_numbers = [cint(i) for i in ijr_numbers]

	meta = {
		'state': { 'default': '', 'values': state_codes },
		'ijr_number': { 'default': default_ijr_number, 'values': ijr_numbers },
		'pillar_or_theme': { 'default': '', 'values': ['', 'overall'] + pillar_slugs + theme_slugs }
	}

	kwargs = _validate_parameters(kwargs, meta)
	return '/state/{state}/ijr-{ijr_number}/{pillar_or_theme}'.format(**kwargs)

def indicator_url(**kwargs):
	'''
	Returns the indicator url based on the given values and fills in default values.
	/indicator/ijr-<ijr_number>/<rank_by>/<cluster>/<view>
	'''
	indicator_ids = frappe.db.get_all('State Indicator', pluck='name')
	default_ijr_number = frappe.db.get_single_value('IJR Settings', 'default_ijr')
	ijr_numbers = ['0'] + frappe.db.get_all('IJR Number', pluck='name', order_by='name asc')
	ijr_numbers = [cint(i) for i in ijr_numbers]

	meta = {
		'indicator_id': { 'default': '', 'values': indicator_ids },
		'ijr_number': { 'default': default_ijr_number, 'values': ijr_numbers },
		'cluster': { 'default': 'large-states', 'values': ['large-states', 'small-states', 'all-states'] },
		'view': { 'default': 'map', 'values': ['map', 'table'] }
	}

	kwargs = _validate_parameters(kwargs, meta)
	return '/indicator/{indicator_id}/ijr-{ijr_number}/{cluster}/{view}'.format(**kwargs)

def _validate_parameters(parameters, meta):
	# validate values, set default if invalid or missing
	for key, desc in meta.items():
		value = parameters.get(key)
		if value is None or value not in desc['values']:
			value = frappe.form_dict.get(key) or desc['default']
		if parameters.get('defaults_only'):
			value = desc['default']
		parameters[key] = value
	return parameters

def get_current_page_url(**kwargs):
	path = frappe.local.request.path
	if path.startswith('/rankings'):
		return rankings_url(**kwargs)
	if path.startswith('/state'):
		return state_url(**kwargs)
	if path.startswith('/indicator'):
		return indicator_url(**kwargs)
