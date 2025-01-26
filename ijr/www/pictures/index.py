# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr


def get_context(context):
	theme = "All"
	if frappe.form_dict.theme:
		theme = frappe.form_dict.theme
	filters = None if theme == "All" else {"theme": frappe.form_dict.theme}
	context.current_theme = theme
	context.pictures = frappe.get_all(
		"IJR Picture", ["name", "title", "image", "theme", "caption"], filters=filters
	)
	context.page_title = theme
	if frappe.form_dict.picture_id:
		picture_id = cstr(frappe.form_dict.picture_id)
		picture = frappe.db.get_value(
			"IJR Picture", picture_id, ["name", "title", "image", "caption"], as_dict=True
		)
		if picture:
			context.metatags = {
				"title": picture.title,
				"image": picture.image,
				"description": (picture.caption or '')[:155],
			}
