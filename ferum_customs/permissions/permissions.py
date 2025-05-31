"""Динамические условия разрешений (permission query conditions).

Функции из этого модуля подключаются в `hooks.py`:
    permission_query_conditions = {
        "service_request": "ferum_customs.permissions.permissions.get_service_request_pqc",
    }
"""

from __future__ import annotations

import frappe


def get_service_request_pqc(user: str) -> dict[str, str] | None:
    """Вернуть фильтры (dict), ограничивающие список заявок для пользователя.

    * Если у пользователя указан `customer` (поле в DocType *User*), он
      видит только заявки своего заказчика.
    * Администратор видит все заявки.
    * Если `customer` отсутствует – ничего не показываем.

    Args:
        user: Имя текущего пользователя.

    Returns:
        dict | None: Словарь фильтров, который Frappe преобразует
        во WHERE-условие. `None` означает отсутствие ограничений.
    """
    if user == "Administrator":
        return None  # без ограничений

    customer = frappe.db.get_value("User", user, "customer")
    if customer:
        # Frappe сам безопасно экранирует словари фильтров
        return {"customer": customer}

    # Если customer не задан – скрываем все записи
    # (альтернативно можно вернуть {'name': ('=', '')})
    return {"name": ("=", "__no_records__")}
