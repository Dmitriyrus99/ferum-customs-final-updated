import frappe

def get_service_request_pqc(user):
    user_doc = frappe.get_doc('User', user)
    if 'Заказчик' in user_doc.get_roles():
        customer = user_doc.customer_link
        if customer:
            return f'customer = {frappe.db.escape(customer)}'
        else:
            return '1=0'
    return None
