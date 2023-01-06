# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

nullable_float_fields = [
	'overall_score',
	'police_score',
	'prisons_score',
	'judiciary_score',
	'legal_aid_score',
	'hr_score',
	'diversity_score',
	'trends_score',
]

class StateRanking(Document):
	def get_valid_dict(self, *args, **kwargs):
		valid_dict = super().get_valid_dict(*args, **kwargs)

		for column in nullable_float_fields:
			if self.get(column) == float('inf'):
				valid_dict[column] = None

		return valid_dict

def on_doctype_update():
	set_columns_to_be_nullable()

def set_columns_to_be_nullable():
	for fieldname in nullable_float_fields:
		frappe.db.sql_ddl(f"ALTER TABLE `tabState Ranking` MODIFY `{fieldname}` decimal(21,9);")
