# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StateIndicatorRawData(Document):
	def get_valid_dict(self, *args, **kwargs):
		valid_dict = super().get_valid_dict(*args, **kwargs)
		if self.raw_data_value == float('inf'):
			valid_dict['raw_data_value'] = None

		return valid_dict


def on_doctype_update():
	set_columns_to_be_nullable()

def set_columns_to_be_nullable():
	frappe.db.sql_ddl("ALTER TABLE `tabState Indicator Raw Data` MODIFY `raw_data_value` decimal(21,9);")
