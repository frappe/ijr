# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from ijr.india_justice_report.doctype.ijr_file.ijr_file import IJRFile
from frappe.utils.response import as_raw
from frappe.database import savepoint

@frappe.whitelist(allow_guest=True)
def download(file_id=None):
	if not file_id:
		return

	# with savepoint():
	file: IJRFile = frappe.get_doc('IJR File', file_id)
	file.track_download()
	frappe.db.commit()

	_file = frappe.get_doc('File', {'file_url': file.file})
	frappe.response.filename = _file.file_name
	frappe.response.filecontent = _file.get_content()
	frappe.response.type = 'download'
	return as_raw()


@frappe.whitelist(allow_guest=True)
def get_indicator_description(indicator_id):
	if not isinstance(indicator_id, str):
		frappe.throw('Invalid indicator id')
	data = frappe.db.get_value('State Indicator', indicator_id, ['long_description', 'description'], as_dict=True)
	return data.get('long_description') or data.get('description') or 'No description available'

	