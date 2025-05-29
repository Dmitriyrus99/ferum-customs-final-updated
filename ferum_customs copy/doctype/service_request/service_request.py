import frappe
from frappe.model.document import Document

class ServiceRequest(Document):
    def validate(self):
        frappe.get_doc('FerumCustoms').validate_service_request(self)
