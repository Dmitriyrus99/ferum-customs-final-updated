import frappe
from frappe.model.document import Document

class ServiceProject(Document):
    def validate(self):
        self.validate_project_object_items_uniqueness()

    def validate_project_object_items_uniqueness(self):
        seen = set()
        for item in self.project_object_items:
            if not item.service_object:
                continue  # возможно, это необязательное поле или еще не заполнено

            if item.service_object in seen:
                frappe.throw(
                    frappe._(f"Duplicate entry for Service Object: {item.service_object}")
                )
            seen.add(item.service_object)
