import frappe
from frappe.model.rename_doc import rename_doc

def execute():
    if frappe.db.exists('DocType', 'Project') and not frappe.db.exists('DocType', 'ServiceProject'):
        rename_doc('DocType', 'Project', 'ServiceProject', force=True)
        frappe.db.commit()
