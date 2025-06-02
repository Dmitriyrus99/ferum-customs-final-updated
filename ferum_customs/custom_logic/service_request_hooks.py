# ferum_customs/ferum_customs/custom_logic/service_request_hooks.py
"""Хуки для DocType *ServiceRequest*."""

from __future__ import annotations
from typing import TYPE_CHECKING, List

import frappe
from frappe import _
from frappe.utils import now

from ..constants import (
    STATUS_VYPOLNENA,
    STATUS_ZAKRYTA,
    ROLE_PROEKTNYJ_MENEDZHER,
    STATUS_OTKRYTA, 
    STATUS_V_RABOTE
    # STATUS_K_VYPOLNENIYU 
)

if TYPE_CHECKING:
    from ..doctype.service_request.service_request import ServiceRequest
    from frappe.model.document import Document as FrappeDocument


# --------------------------------------------------------------------------- #
#                               Doc Events                                  #
# --------------------------------------------------------------------------- #

def validate(doc: "ServiceRequest", method: str | None = None) -> None:
    """
    Вызывается Frappe перед сохранением `ServiceRequest`.
    Проверяем бизнес-правила.
    """
    if doc.status == STATUS_VYPOLNENA and not doc.get("custom_linked_report"): # ИЗМЕНЕНО
        frappe.throw(_("Нельзя отметить заявку выполненной без связанного отчёта о выполненных работах (Service Report)."))

    if doc.status == STATUS_VYPOLNENA and not doc.get("completed_on"):
        if doc.meta.has_field("completed_on"): # completed_on - стандартное поле, его не меняем
            doc.completed_on = now()
        else:
            frappe.logger(__name__).warning(
                f"ServiceRequest: {doc.name}. Field 'completed_on' is missing in DocType, but validation logic expects it."
            )

    if doc.get("custom_project") and not doc.get("custom_customer"): # ИЗМЕНЕНО x2
        customer_from_project = frappe.db.get_value("ServiceProject", doc.custom_project, "customer") # ИЗМЕНЕНО
        if customer_from_project:
            doc.custom_customer = customer_from_project # ИЗМЕНЕНО
        else:
            frappe.throw(
                _("Клиент должен быть указан для заявки на обслуживание, или выбранный проект ({0}) должен иметь связанного клиента.").format(doc.custom_project) # ИЗМЕНЕНО
            )

    if not doc.get("custom_customer") and doc.get("custom_service_object_link"): # ИЗМЕНЕНО x2
        customer_from_so = frappe.db.get_value("ServiceObject", doc.custom_service_object_link, "customer") # ИЗМЕНЕНО
        if customer_from_so:
            doc.custom_customer = customer_from_so # ИЗМЕНЕНО


    # if doc.status in [STATUS_V_RABOTE] and not doc.get("custom_assigned_engineer"): # ИЗМЕНЕНО (Пример)
    #     frappe.throw(_("Необходимо назначить инженера для заявки в статусе '{0}'.").format(doc.status))


def on_update_after_submit(doc: "ServiceRequest", method: str | None = None) -> None:
    if doc.status == STATUS_ZAKRYTA:
        _notify_project_manager(doc) # Внутренние поля doc (name, subject и т.д.) не меняются

def prevent_deletion_with_links(doc: "ServiceRequest", method: str | None = None) -> None:
    if doc.name:
        linked_reports = frappe.db.exists("ServiceReport", {"service_request": doc.name}) # service_request в ServiceReport стандартное, не меняем
        if linked_reports:
            frappe.throw(
                _("Нельзя удалить заявку {0}, так как на нее ссылаются один или несколько отчетов о выполненных работах (например, {1}).").format(doc.name, linked_reports)
            )

# --------------------------------------------------------------------------- #
#                           Whitelisted Methods                             #
# --------------------------------------------------------------------------- #

@frappe.whitelist()
def get_engineers_for_object(service_object_name: str) -> List[str]:
    # Эта функция принимает имя объекта, а не документ ServiceRequest, поэтому здесь нет изменений fieldname
    if not service_object_name:
        return []

    engineers: List[str] = []
    try:
        service_object_doc: "FrappeDocument" = frappe.get_doc("ServiceObject", service_object_name)

        assigned_engineers_table = service_object_doc.get("assigned_engineers") 
        if assigned_engineers_table and isinstance(assigned_engineers_table, list):
            for entry in assigned_engineers_table:
                if entry.get("engineer"):
                    engineers.append(entry.engineer)

    except frappe.DoesNotExistError:
        frappe.logger(__name__).info(f"ServiceObject '{service_object_name}' not found while trying to get assigned engineers.")
        return [] 
    except Exception as e:
        frappe.logger(__name__).error(
            f"Error fetching engineers for ServiceObject '{service_object_name}': {e}",
            exc_info=True
        )
        return []

    return list(set(engineers))

# --------------------------------------------------------------------------- #
#                               Вспомогательное                               #
# --------------------------------------------------------------------------- #

def _notify_project_manager(doc: "ServiceRequest") -> None:
    try:
        recipients = frappe.get_all(
            "User",
            filters={"enabled": 1, "user_type": "System User", "roles.role": ROLE_PROEKTNYJ_MENEDZHER},
            pluck="name",
            distinct=True,
        )

        if not recipients:
            frappe.logger(__name__).warning(
                f"No recipients found with role '{ROLE_PROEKTNYJ_MENEDZHER}' for Service Request '{doc.name}' closure notification."
            )
            return

        subject = _("Заявка на обслуживание {0} закрыта").format(doc.name)
        # Используем стандартные поля doc.name, doc.subject, doc.status, doc.custom_customer (если нужно в тексте)
        message_body_parts = [
            _("Заявка на обслуживание {0} была переведена в статус «Закрыта».").format(doc.name)
        ]
        if doc.subject:
             message_body_parts.append(_("Тема: {0}").format(doc.subject))
        if doc.get("custom_customer"): # ИЗМЕНЕНО
             message_body_parts.append(_("Клиент: {0}").format(frappe.get_cached_value("Customer", doc.custom_customer, "customer_name") or doc.custom_customer)) # ИЗМЕНЕНО

        message_body = "\n".join(message_body_parts)

        link_to_request = frappe.utils.get_link_to_form('ServiceRequest', doc.name)

        message = f"""<p>{message_body.replace("\n", "<br>")}</p>
<p><a href='{link_to_request}'>{_('Просмотреть заявку на обслуживание')}</a></p>"""

        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            reference_doctype="ServiceRequest",
            reference_name=doc.name,
            now=True 
        )
        frappe.logger(__name__).info(f"Sent closure notification for ServiceRequest '{doc.name}' to project managers.")

    except Exception as e:
        frappe.logger(__name__).error(
            f"Failed to send closure notification for ServiceRequest '{doc.name}': {e}",
            exc_info=True
        )