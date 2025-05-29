import frappe
from frappe import _
from ..constants import STATUS_VYPOLNENA, STATUS_ZAKRYTA, STATUS_OTMENENA, ROLE_PROEKTNYJ_MENEDZHER, ROLE_INZHENER

def validate_service_request(doc, method):
    """
    Validate Service Request:
    - Cannot close (Выполнена, Закрыта) without a linked Service Report.
    """
    if doc.status in (STATUS_VYPOLNENA, STATUS_ZAKRYTA) and not doc.linked_report:
        frappe.throw(_("Нельзя закрыть заявку без привязанного Service Report"))

def handle_status_update(doc, method):
    """
    If Service Request status changes to 'Отменена' (Cancelled),
    remove the link to the Service Report.
    """
    if doc.status == STATUS_OTMENENA and doc.linked_report:
        doc.db_set("linked_report", None, update_modified=False)

def prevent_deletion_with_links(doc, method):
    """
    Prevent deletion of Service Request if it is linked to a Service Report
    or a Sales Invoice.
    """
    if doc.linked_report:
        frappe.throw(_("Нельзя удалить заявку: к ней привязан Service Report"))

    if frappe.db.exists("Sales Invoice", {"service_request_ref": doc.name}):
        frappe.throw(_("Нельзя удалить заявку: к ней привязан счет продаж (Sales Invoice)"))

@frappe.whitelist()
def get_engineers_for_object(service_object):
    """
    Get a list of engineers (User IDs) assigned to a specific Service Object.
    This method is whitelisted for use in client scripts (e.g., via frappe.call).
    Includes a basic permission check.
    """
    # Basic permission check.
    # Consider if other roles, like "Инженер" (ROLE_INZHENER), should also have access,
    # especially if they need to select themselves or view assignments.
    # For now, restricting to "Проектный менеджер" as per initial secure approach.
    if ROLE_PROEKTNYJ_MENEDZHER not in frappe.get_roles():
        # A more specific check could be added here if engineers are allowed to see this list
        # for objects they are related to, or if they are selecting themselves.
        # Example: if not (ROLE_PROEKTNYJ_MENEDZHER in frappe.get_roles() or (ROLE_INZHENER in frappe.get_roles() and some_condition_for_engineer_access)):
        frappe.throw(_("Недостаточно прав для получения списка инженеров."), frappe.PermissionError)

    if not service_object:
        return []

    engineers = frappe.get_all(
        "AssignedEngineerItem",
        # Corrected parenttype to "ServiceObject" (no space)
        filters={"parenttype": "ServiceObject", "parent": service_object},
        pluck="engineer"
    )
    return engineers
