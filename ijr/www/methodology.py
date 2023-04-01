# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe


def get_context(context):
	context.content = frappe.read_file("../apps/ijr/ijr/www/_methodology.md")