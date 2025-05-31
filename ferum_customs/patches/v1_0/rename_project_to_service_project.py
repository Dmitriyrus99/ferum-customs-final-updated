# ferum_customs/patches/v1_0/rename_project_to_service_project.py
import frappe
from frappe.model.rename_doc import rename_doc

def execute():
    """Renames DocType 'Project' to 'service_project' if it exists and 'service_project' doesn't."""
    if frappe.db.exists('DocType', 'Project') and not frappe.db.exists('DocType', 'service_project'):
        frappe.print("Renaming DocType 'Project' to 'service_project'...")
        try:
            rename_doc('DocType', 'Project', 'service_project', force=True, ignore_permissions=True)
            frappe.print("Successfully renamed 'Project' to 'service_project'.")
        except Exception as e:
            frappe.log_error(f"Error renaming DocType Project to ServiceProject: {e}", "Patch Error")
            frappe.print(f"Error during rename: {e}")
        # frappe.db.commit() # Usually not needed as patches run in their own transaction.
                          # Keep if there's a specific reason for intermediate commit in a more complex patch.
    elif not frappe.db.exists('DocType', 'Project'):
        frappe.print("DocType 'Project' does not exist. Skipping rename.")
    elif frappe.db.exists('DocType', 'service_project'):
        frappe.print("DocType 'service_project' already exists. Skipping rename.")