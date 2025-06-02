# ferum_customs/install.py
"""
Код, выполняемый после установки приложения `ferum_customs`.

Может использоваться для создания начальных данных, ролей,
пользовательских полей (хотя фикстуры предпочтительнее для этого),
или других настроек, необходимых для работы приложения.
"""
import frappe
from frappe import _ # Для возможных сообщений

# Импорт констант ролей, если они используются
# from .constants import (
#     ROLE_PROEKTNYJ_MENEDZHER,
#     ROLE_OFIS_MENEDZHER,
#     ROLE_INZHENER,
#     ROLE_ZAKAZCHIK
# )

def after_install() -> None:
    """
    Вызывается один раз после успешной установки приложения.
    """
    frappe.db.commit() # Коммит предыдущих транзакций перед началом операций в after_install, если необходимо

    # Создание кастомных ролей, если они еще не существуют.
    # Это также можно сделать через fixtures (fixtures/role.json), что является предпочтительным способом.
    # Логика здесь дублирует то, что может быть в role.json.
    # Оставляем для примера, но рекомендуется использовать фикстуры.
    
    # Список ролей для создания (должен совпадать с constants.py и fixtures/role.json)
    # TODO: Согласовать с fixtures/role.json и constants.py
    custom_roles = [
        "Проектный менеджер", 
        "Офис-менеджер", 
        "Инженер", 
        "Заказчик"
    ]

    existing_roles = {d.name for d in frappe.get_all("Role", fields=["name"])}
    
    roles_created_count = 0
    for role_name in custom_roles:
        if role_name not in existing_roles:
            try:
                role = frappe.new_doc("Role")
                role.role_name = role_name
                # Можно установить другие свойства роли, если необходимо
                # role.desk_access = 1
                # role.is_custom = 1 # Если это кастомная роль
                role.insert(ignore_permissions=True) # ignore_permissions может потребоваться
                roles_created_count += 1
                frappe.logger(__name__).info(f"Role '{role_name}' created successfully during app installation.")
            except Exception as e:
                frappe.logger(__name__).error(f"Failed to create role '{role_name}' during app installation: {e}", exc_info=True)
    
    if roles_created_count > 0:
        frappe.db.commit() # Коммит после создания ролей
        frappe.msgprint(
            _("{0} custom role(s) checked/created for Ferum Customs.").format(roles_created_count),
            title=_("Installation Setup"),
            indicator="green"
        )
    else:
        frappe.logger(__name__).info("All custom roles for Ferum Customs already exist.")


    # Пример: Добавление пользовательских полей программно (обычно делается через fixtures/custom_field.json)
    # add_custom_fields()

    # Пример: Установка прав доступа по умолчанию (обычно делается через fixtures/custom_docperm.json)
    # setup_default_permissions()

    # Пример: Создание начальных данных
    # create_initial_data()

    frappe.db.commit() # Финальный коммит
    frappe.msgprint(
        _("Ferum Customs application installed successfully. Please check system settings and user roles."),
        title=_("Installation Complete"),
        indicator="green"
    )

# Пример функции для добавления Custom Fields (не рекомендуется, лучше фикстуры)
# def add_custom_fields():
#     if not frappe.db.exists("Custom Field", {"dt": "User", "fieldname": "custom_user_department"}):
#         frappe.get_doc({
#             "doctype": "Custom Field",
#             "dt": "User",
#             "fieldname": "custom_user_department",
#             "label": "Department (Custom)",
#             "fieldtype": "Link",
#             "options": "Department",
#             "insert_after": "role_profile_name" # Пример
#         }).insert()

# Пример функции для создания начальных данных
# def create_initial_data():
#     if not frappe.db.exists("ServiceType", {"service_type_name": "Standard Maintenance"}): # Пример DocType
#         frappe.get_doc({
#             "doctype": "ServiceType",
#             "service_type_name": "Standard Maintenance",
#             "default_duration_hours": 2
#         }).insert()