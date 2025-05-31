"""Хуки для DocType *ServiceReport*.

* Проверяем корректность привязки к заявке (validate).
* После отправки отчёта обновляем связанную `service_request`
  через `update_linked_request_on_submit`.
"""

from __future__ import annotations

import frappe
from frappe import _

from ..constants import STATUS_VYPOLNENA


# --------------------------------------------------------------------------- #
#                               DocType events                                #
# --------------------------------------------------------------------------- #
def validate(doc, *_):
    """Отчёт должен ссылаться на заявку со статусом «Выполнена»."""
    if not doc.service_request:
        frappe.throw(_("Не выбрана связанная Service Request."))

    req_status = frappe.db.get_value("service_request", doc.service_request, "status")
    if req_status != STATUS_VYPOLNENA:
        frappe.throw(_("Отчёт можно привязать только к заявке в статусе «Выполнена»."))
    # Можно добавить дополнительные проверки содержимого отчёта


def update_linked_request_on_submit(doc, *_):
    """После submit отчёта обновляем связанную service_request.

    Действия:
    1. Записываем ссылку на отчёт в поле `service_report`.
    2. Если заявка ещё не помечена «Выполнена», переводим её в этот статус.
    """
    if not doc.service_request:
        # отчёт без заявки – ничего делать не нужно
        return

    req = frappe.get_doc("service_request", doc.service_request)
    changed = False

    if not req.get("service_report"):
        req.service_report = doc.name
        changed = True

    if req.status != STATUS_VYPOLNENA:
        req.status = STATUS_VYPOLNENA
        changed = True

    if changed:
        # сохраняем без триггера повторного submit-workflow
        req.save(ignore_permissions=True)
