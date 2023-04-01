# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.formatters import format_value
from ijr.jinja_helpers import indicator_url

def get_context(context):
	if not frappe.form_dict.indicator_id and frappe.form_dict.pillar:
		result = frappe.qb.get_query('State Indicator', filters={'pillar.slug': frappe.form_dict.pillar}, fields=['name']).run(as_dict=1)
		indicator_id = result[0].name if result else None

		if indicator_id:
			frappe.flags.redirect_location = indicator_url(
				indicator_id=indicator_id,
				ijr_number=3,
				cluster='large-states',
				view='map'
			)
			raise frappe.Redirect

	if not frappe.form_dict.indicator_id:
		frappe.throw('Indicator not found', frappe.PageDoesNotExistError)

	if frappe.form_dict.indicator_id and not frappe.db.exists('State Indicator', frappe.form_dict.indicator_id):
		frappe.throw('Indicator not found', frappe.PageDoesNotExistError)


	if not (frappe.form_dict.ijr_number or frappe.form_dict.view or frappe.form_dict.cluster):
		url = indicator_url(
			indicator_id=frappe.form_dict.indicator_id,
			ijr_number=3,
			cluster='large-states',
			view='map'
		)
		frappe.flags.redirect_location = url
		raise frappe.Redirect

	view = frappe.form_dict.view or 'map'
	indicator_id = frappe.form_dict.indicator_id
	ijr_number = frappe.utils.cint(frappe.form_dict.ijr_number or '3')
	default_cluster = 'large-states' if view == 'map' else 'all'
	cluster = frappe.form_dict.cluster or default_cluster

	order_by = ''
	filters = {'ijr_score': ['is', 'set']}
	if view == 'table':
		filters['indicator_id'] = indicator_id
		order_by = 'state asc, ijr_number asc'
	elif view == 'map':
		filters['indicator_id'] = indicator_id
		filters['ijr_number'] = ijr_number
		order_by = 'ijr_score desc, `order` asc'

	if cluster == 'large-states':
		filters['cluster'] = 'Large and mid-sized states'
	if cluster == 'small-states':
		filters['cluster'] = 'Small states'
	# if cluster == 'all':
	# 	filters['cluster'] = None

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
			{'label': 'Score', 'id': 'ijr_score', 'format': '''return Number(d.ijr_score).toFixed(2)''', 'align': 'center', 'hide_condition': cluster == 'all'},
		]
		if context.indicator_data:
			for d in context.indicator_data[0].raw_data:
				context.columns.append({
					'label': f'{d.raw_data_name} ({d.raw_data_unit})',
					'id': d.raw_data_name,
					'align': 'center',
					'wrapText': 1
				})
			for row in context.indicator_data:
				for d in row.raw_data:
					row[d.raw_data_name] = d.raw_data_value
					row[d.raw_data_name + '_formatted'] = format_value(d.raw_data_value, {
						'fieldtype': 'Float',
						'precision': d.raw_data_value_decimals or 4
					})

	indicator = frappe.get_doc('State Indicator', indicator_id)

	context.indicator = indicator
	context.title = f'{indicator.indicator_name} | India Justice Report'
	context.description = indicator.description
	context.indicator_pillar = indicator.pillar
	context.indicator_pillar_slug = frappe.db.get_value('Pillar', indicator.pillar, 'slug')
	context.raw_data = get_raw_data_by_state(indicator_id)
	context.indicator_id = indicator_id
	context.view = view
	context.ijr_number = ijr_number
	context.cluster = cluster
	context.no_cache = 1


def indicator_rankings_data(filters, order_by):
	data = frappe.get_all('State Indicator Data',
		filters=filters,
		fields=['*'],
		order_by=order_by
	)

	# prev ijr data for comparison
	prev_ijr_data_by_state = {}
	if filters.get('ijr_number'):
		prev_ijr_filters = filters.copy().update({'ijr_number': filters.get('ijr_number') - 1})
		prev_ijr_data = frappe.get_all('State Indicator Data',
			filters=prev_ijr_filters,
			fields=['*'],
			order_by=order_by
		)
		for d in prev_ijr_data:
			prev_ijr_data_by_state[d.state] = d

	for d in data:
		d.ijr_score_color = ['', 'var(--best)', 'var(--middle)', 'var(--worst)'][d.color_code or 0]
		# delta
		prev_ijr_score = prev_ijr_data_by_state.get(d.state, {}).get('ijr_score', 0)
		if prev_ijr_score is not None and d.ijr_score is not None:
			d.ijr_score_delta = d.ijr_score - prev_ijr_score
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

		raw_data_value = format_value(r.raw_data_value, {
			'fieldtype': 'Float',
			'precision': r.raw_data_value_decimals or None
		})
		data[f'ijr_{r.ijr_number}_value'] = raw_data_value
		if r.ijr_number == 1:
			raw_data_with_all_ijrs.setdefault(r.state, []).append(data)
	return raw_data_with_all_ijrs
