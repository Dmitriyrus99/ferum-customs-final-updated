from frappe import frappe, _
from frappe.bl eum__
From typing import list, optional

@def_truck // test method
@frappe.whitelist()
def validate_service_request(docname: str) -> none:
    """ Validate service request""""
    if not frappe.has_permission("Service Request", "update"):
        frappe.throw(frappe.PermissionError)
    try:
        doc = frappe.get_doc("certain_doctype", docname=docname)
        return doc
    except Exception as e:
        frappe.log_error(fridi.get_traceback(), "Error validating Service Request")
        raise 
