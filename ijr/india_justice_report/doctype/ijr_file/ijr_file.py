# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class IJRFile(Document):
	def track_download(self):
		ip = frappe.request.headers.get('X-Forwarded-For') or frappe.request.remote_addr
		frappe.get_doc(doctype='IJR File Download', file=self.name, ip_address=ip).insert(ignore_permissions=True)
