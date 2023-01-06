# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StateIndicatorData(Document):
	def get_valid_dict(self, *args, **kwargs):
		valid_dict = super().get_valid_dict(*args, **kwargs)
		if self.indicator_value == float('inf'):
			valid_dict['indicator_value'] = None

		if self.ijr_score == float('inf'):
			valid_dict['ijr_score'] = None

		return valid_dict


def on_doctype_update():
	set_columns_to_be_nullable()

def set_columns_to_be_nullable():
	frappe.db.sql_ddl("ALTER TABLE `tabState Indicator Data` MODIFY `indicator_value` decimal(21,9);")
	frappe.db.sql_ddl("ALTER TABLE `tabState Indicator Data` MODIFY `ijr_score` decimal(21,9);")
