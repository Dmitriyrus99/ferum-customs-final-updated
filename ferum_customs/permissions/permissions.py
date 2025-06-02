# ferum_customs/permissions/permissions.py
"""
Динамические условия для запросов разрешений (Permission Query Conditions).
"""

from __future__ import annotations
from typing import Dict, List, Union, Optional 

import frappe
from frappe import _ 
from ..constants import ROLE_ADMINISTRATOR, ROLE_ZAKAZCHIK 

PQCConditionValue = Union[str, List[Union[str, List[str]]], Dict[str, str]]
PQCConditions = Dict[str, PQCConditionValue]


def get_service_request_pqc(user: Optional[str] = None) -> Optional[PQCConditions]:
    if user is None:
        user = frappe.session.user

    if user == "Administrator" or frappe.has_role("System Manager", user):
         return None 

    try:
        user_doc = frappe.get_cached_doc("User", user) 
    except frappe.DoesNotExistError:
        frappe.logger(__name__).warning(f"User '{user}' not found while applying PQC for ServiceRequest.")
        return {"name": ("=", f"__no_records_user_not_found_{user}")} 

    # Поле 'customer' в User DocType должно быть кастомным, если вы его используете для PQC.
    # Предположим, оно называется 'custom_linked_customer_for_user' в User.
    # user_linked_customer = user_doc.get("custom_linked_customer_for_user") 
    # Если вы используете стандартное поле 'company' для привязки к клиенту (что нетипично) или другое, адаптируйте.
    # Для примера, если пользователь-заказчик привязан к документу Customer через поле 'party' (стандартное для Portal User)
    # или через кастомное поле 'customer' в User.
    user_linked_customer = user_doc.get("customer") # Предполагаем, что в User есть поле 'customer' (Link to Customer)

    is_customer_role = frappe.has_role(ROLE_ZAKAZCHIK, user)

    if is_customer_role and user_linked_customer:
        # Пользователь с ролью "Заказчик" и привязанным клиентом видит только заявки своего клиента.
        # ServiceRequest теперь имеет поле custom_customer
        return {"custom_customer": user_linked_customer} # ИЗМЕНЕНО

    return None