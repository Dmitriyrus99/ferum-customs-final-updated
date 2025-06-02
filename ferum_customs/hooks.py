# ferum_customs/hooks.py
try:
    from .ferum_customs import __version__ as app_version
except ImportError:
    try:
        from . import __version__ as app_version
    except ImportError:
        app_version = "1.0.0"

from frappe import _

app_name = "ferum_customs"
app_title = "Ferum Customizations"
app_publisher = "Ferum LLC"
app_description = "Specific customizations for ERPNext for Ferum operations."
app_email = "support@ferum.ru"
app_license = "MIT"

app_include_js = ["ferum_customs.bundle.js"]

doc_events = {
    "ServiceRequest": {
        "validate": "ferum_customs.custom_logic.service_request_hooks.validate",
        "on_update_after_submit": "ferum_customs.custom_logic.service_request_hooks.on_update_after_submit",
        "on_trash": "ferum_customs.custom_logic.service_request_hooks.prevent_deletion_with_links"
    },
    "ServiceReport": {
        "validate": "ferum_customs.custom_logic.service_report_hooks.validate",
        "on_submit": "ferum_customs.custom_logic.service_report_hooks.on_submit",
    },
    "ServiceObject": {
        "validate": "ferum_customs.custom_logic.service_object_hooks.validate",
    },
    "PayrollEntryCustom": {
        "validate": "ferum_customs.custom_logic.payroll_entry_hooks.validate",
        "before_save": "ferum_customs.custom_logic.payroll_entry_hooks.before_save",
    },
    "CustomAttachment": {
         "on_trash": "ferum_customs.custom_logic.file_attachment_utils.on_custom_attachment_trash"
    },
}

whitelisted_methods = [
    "ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object",
    "ferum_customs.utils.utils.get_engineers_for_service_object",
]

permission_query_conditions = {
    "ServiceRequest": "ferum_customs.permissions.permissions.get_service_request_pqc",
}

# --- Test 1: Only custom_docperm ---
fixtures = [
    "custom_docperm",
]
# --- End Test 1 ---

notification_config = "ferum_customs.notifications.notifications.get_notification_config"