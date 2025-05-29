import frappe
from frappe import _

def prevent_object_deletion(doc, method):
    if frappe.db.exists("ServiceRequest", {"service_object": doc.name}):
        frappe.throw(_("Нельзя удалить объект: к нему существуют заявки"))
