# ferum_customs/ferum_customs/custom_logic/service_report_hooks.py
"""Хуки для DocType *ServiceReport*.

* Проверяем корректность привязки к заявке (validate).
* После отправки отчёта обновляем связанную `ServiceRequest`
  через `on_submit`.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import frappe
from frappe import _

# Убедитесь, что этот путь корректен
# Предполагается, что constants.py находится в ferum_customs/ferum_customs/constants.py
from ..constants import STATUS_VYPOLNENA

if TYPE_CHECKING:
    # Замените на корректные пути к вашим DocType, если необходимо
    from ..doctype.service_report.service_report import ServiceReport
    from ..doctype.service_request.service_request import ServiceRequest
    # from frappe.model.document import Document # Общий тип для документов
    # ServiceReport = Document
    # ServiceRequest = Document

# --------------------------------------------------------------------------- #
#                           DocType events                                    #
# --------------------------------------------------------------------------- #

def validate(doc: "ServiceReport", method: str | None = None) -> None:
    """
    Проверяет, что отчёт ссылается на существующую заявку со статусом «Выполнена».
    Вызывается перед сохранением ServiceReport.

    Args:
        doc: Экземпляр документа ServiceReport.
        method: Имя вызвавшего метода (например, "validate").

    Raises:
        frappe.ValidationError: Если нарушены бизнес-правила.
    """
    if not doc.service_request:
        frappe.throw(_("Не выбрана связанная заявка на обслуживание (Service Request)."))

    # Проверяем, существует ли такая заявка, чтобы избежать ошибок при get_value
    if not frappe.db.exists("ServiceRequest", doc.service_request):
        frappe.throw(
            _("Связанная заявка на обслуживание (Service Request) '{0}' не найдена.").format(doc.service_request)
        )

    # TODO: Verify fieldname 'status' in ServiceRequest DocType JSON
    req_status = frappe.db.get_value("ServiceRequest", doc.service_request, "status")
    
    if req_status is None:
        # Этого не должно произойти, если frappe.db.exists прошло, но для надежности
        frappe.logger(__name__).error(
            f"Could not retrieve status for ServiceRequest '{doc.service_request}' linked to ServiceReport '{doc.name}'."
        )
        frappe.throw(
            _("Не удалось получить статус для связанной заявки на обслуживание '{0}'. Обратитесь к администратору.").format(doc.service_request)
        )

    if req_status != STATUS_VYPOLNENA:
        frappe.throw(
            _("Отчёт можно привязать только к заявке в статусе «{0}». Текущий статус заявки «{1}».").format(
                STATUS_VYPOLNENA, req_status
            )
        )
    
    # Сюда можно добавить дополнительные проверки содержимого отчёта, если необходимо.
    # Например, что все обязательные поля в самом отчете заполнены.
    # if not doc.get("work_done_summary"): # Пример
    #     frappe.throw(_("Поле 'Описание выполненных работ' в отчете обязательно для заполнения."))

def on_submit(doc: "ServiceReport", method: str | None = None) -> None:
    """
    После отправки (submit) отчёта обновляет связанную ServiceRequest.

    Действия:
    1. Записывает ссылку на этот отчёт в поле `linked_report` связанной ServiceRequest.
       (Убедитесь, что имя поля `linked_report` в ServiceRequest указано верно).
    2. Убеждается, что статус связанной заявки установлен в «Выполнена».

    Args:
        doc: Экземпляр документа ServiceReport.
        method: Имя вызвавшего метода (например, "on_submit").
    """
    if not doc.service_request:
        # Отчёт без заявки – ничего делать не нужно.
        # Эта ситуация не должна возникнуть, если validate отработал корректно.
        frappe.logger(__name__).warning(
            f"ServiceReport '{doc.name}' submitted without a service_request link. This should have been caught by validate hook."
        )
        return

    try:
        # TODO: Verify fieldname 'linked_report' in ServiceRequest DocType JSON
        REPORT_LINK_FIELD_ON_REQUEST = "linked_report" 
        
        req: "ServiceRequest" = frappe.get_doc("ServiceRequest", doc.service_request)
        
        changed_fields = {}

        if not req.get(REPORT_LINK_FIELD_ON_REQUEST) or req.get(REPORT_LINK_FIELD_ON_REQUEST) != doc.name:
            changed_fields[REPORT_LINK_FIELD_ON_REQUEST] = doc.name
        
        # Этот блок является дополнительной защитой.
        # `validate` должен был уже обеспечить, что статус `STATUS_VYPOLNENA`.
        if req.status != STATUS_VYPOLNENA:
            changed_fields["status"] = STATUS_VYPOLNENA
            # Если вы также хотите обновить дату выполнения ServiceRequest здесь:
            # TODO: Verify fieldname 'completed_on' in ServiceRequest DocType JSON
            # if req.meta.has_field("completed_on") and not req.get("completed_on"):
            #    from frappe.utils import now
            #    changed_fields["completed_on"] = now()

        if changed_fields:
            # Обновляем поля без вызова save(), чтобы избежать рекурсивных хуков и воркфлоу, если не требуется
            # Используем db_set для submitted документов, если это возможно и логично
            # req.db_set(changed_fields, notify=True) # notify=True может быть полезно для обновления UI
            # Альтернативно, если нужны хуки ServiceRequest (кроме on_submit/on_update):
            for field, value in changed_fields.items():
                req.set(field, value)
            req.save(ignore_permissions=True) # Сохраняем изменения в ServiceRequest.
            
            frappe.msgprint(
                _("Связанная заявка на обслуживание {0} была обновлена.").format(req.name),
                indicator="green",
                alert=True
            )
            frappe.logger(__name__).info(
                f"ServiceRequest '{req.name}' updated from ServiceReport '{doc.name}'. Changes: {changed_fields}"
            )

    except frappe.DoesNotExistError:
        frappe.logger(__name__).error(
            f"ServiceRequest '{doc.service_request}' linked in ServiceReport '{doc.name}' not found during on_submit.",
            exc_info=True
        )
        # Можно рассмотреть frappe.throw, если это критическая ошибка
    except Exception as e:
        frappe.logger(__name__).error(
            f"Error updating linked ServiceRequest '{doc.service_request}' from ServiceReport '{doc.name}': {e}",
            exc_info=True
        )
        frappe.throw(
            _("Произошла ошибка при обновлении связанной заявки на обслуживание. Обратитесь к администратору.")
        )