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
	indicators = frappe.db.get_all('State Indicator Data',
		fields=['distinct(`indicator_id`) as value', 'indicator_name as label', 'pillar', 'theme'],
		order_by='indicator_id asc'
	)
	indicators_by_pillars = {}
	for i in indicators:
		indicators_by_pillars.setdefault(i.pillar, []).append(i)

	indicators_by_pillars_and_themes = {}
	for pillar, indicators in indicators_by_pillars.items():
		indicators_by_pillars_and_themes[pillar] = {}
		for i in indicators:
			indicators_by_pillars_and_themes[pillar].setdefault(i.theme, []).append(i)

	return indicators_by_pillars_and_themes

def get_color(color_code):
	color_code = cint(color_code)
	color_map = {
		1: 'var(--best)',
		2: 'var(--middle)',
		3: 'var(--worst)'
	}
	return color_map.get(color_code)
