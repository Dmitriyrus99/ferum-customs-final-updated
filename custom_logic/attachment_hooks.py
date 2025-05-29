import os
import frappe

@frappe.whitelist()
def delete_attachment_file(attachment_name):
    file_path = frappe.get_site_path('public', 'files', attachment_name)
    try:
        os.remove(file_path)
    except OSError:
        frappe.throw(f"Unable to delete file {attachment_name}")
