from frappe import _, whitelist
from frappe.exceptions import PermissionError
from typing import Optional

@whitelist()
def validate_service_request(docname: str) -> Optional[dict]:
    """Validate service request""""
    if not frappe.has_permission( "Service Request", "update"):
        frappe.throw(_("Not permitted"), PermissionError)
    try:
        doc = frappe.get_doc("Service Request", docname)
        return doc.as_dict()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error validating Service Request")
        raise