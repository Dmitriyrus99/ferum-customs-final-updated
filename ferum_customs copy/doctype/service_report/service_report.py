import frappe
from frappe.model.document import Document

class ServiceReport(Document):
    def validate(self):
        self.validate_work_items_description()

    def validate_work_items_description(self):
        for item in self.work_items:
            if not item.description:
                frappe.throw('Description is mandatory for all work items.')
