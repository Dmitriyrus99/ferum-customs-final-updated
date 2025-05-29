import frappe
from ferum_customs.constants import STATUS_COMPLETED

def update_linked_request_on_submit(doc, method):
    """После submit ServiceReport:
       1) записать ссылку в ServiceRequest.linked_report
       2) сменить статус заявки на 'Выполнена'
    """
    if not doc.service_request:
        return

    req = frappe.get_doc("ServiceRequest", doc.service_request)
    req.db_set("linked_report", doc.name, update_modified=False)
    if req.status not in (STATUS_COMPLETED, "Закрыта"):
        req.db_set("status", STATUS_COMPLETED, update_modified=False)
    # commit removed: managed by framework
