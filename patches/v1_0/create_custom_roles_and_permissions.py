import frappe

def execute():
    roles = ['Проектный менеджер', 'Офис-менеджер', 'Инженер', 'Заказчик']
    for role in roles:
        if not frappe.db.exists('Role', role):
            frappe.get_doc({'doctype': 'Role', 'role_name': role}).insert()
    # Setup permissions if needed
