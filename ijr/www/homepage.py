# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	context.facts = frappe.db.get_all('IJR Homepage Fact', filters={'published': 1}, fields=['*'], order_by='creation asc, `order` asc')