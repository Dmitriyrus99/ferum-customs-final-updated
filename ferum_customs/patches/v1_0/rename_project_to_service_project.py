# ferum_customs/patches/v1_0/rename_project_to_service_project.py
import frappe
from frappe.model.rename_doc import rename_doc

def execute():
    """Renames DocType 'Project' to 'ServiceProject' if it exists and 'ServiceProject' doesn't."""
    if frappe.db.exists('DocType', 'Project') and not frappe.db.exists('DocType', 'ServiceProject'):
        frappe.print("Renaming DocType 'Project' to 'ServiceProject'...")
        try:
            rename_doc('DocType', 'Project', 'ServiceProject', force=True, ignore_permissions=True)
            frappe.print("Successfully renamed 'Project' to 'ServiceProject'.")
        except Exception as e:
            frappe.log_error(f"Error renaming DocType Project to ServiceProject: {e}", "Patch Error")
            frappe.print(f"Error during rename: {e}")
        # frappe.db.commit() # Usually not needed as patches run in their own transaction.
                          # Keep if there's a specific reason for intermediate commit in a more complex patch.
    elif not frappe.db.exists('DocType', 'Project'):
        frappe.print("DocType 'Project' does not exist. Skipping rename.")
    elif frappe.db.exists('DocType', 'ServiceProject'):
        frappe.print("DocType 'ServiceProject' already exists. Skipping rename.")