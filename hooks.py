app_name = 'ferum_customs'
app_title = 'Ferum Customizations'
app_publisher = 'Ferum LLC'
app_description = 'Ferum-specific customizations for ERPNext'
app_email = 'support@ferum.ru'
app_license = 'MIT'

# ───────────────────────────────────────── doc_events ──────────────────────────────────────────
doc_events = {
    "ServiceReport": {
        "on_submit": "ferum_customs.custom_logic.service_report_hooks.update_linked_request_on_submit",
        # "validate": "ferum_customs.custom_logic.service_report_hooks.validate_service_report",
    },
    "ServiceRequest": {
        "validate": "ferum_customs.custom_logic.service_request_hooks.validate_service_request",
        "on_update": "ferum_customs.custom_logic.service_request_hooks.handle_status_update",
        "on_trash": "ferum_customs.custom_logic.service_request_hooks.prevent_deletion_with_links",
    },
    "ServiceObject": {
        "on_trash": "ferum_customs.custom_logic.service_object_hooks.prevent_object_deletion",
    },
    "PayrollEntryCustom": {
        "before_save": "ferum_customs.custom_logic.payroll_entry_hooks.calculate_total_payable",
    },
    "CustomAttachment": {
        "on_trash": "ferum_customs.custom_logic.attachment_hooks.delete_attachment_file",
    },
}

# ───────────────────────────────── permission queries / notifications ──────────────────────────
permission_query_conditions = {
    # Corrected path: removed duplicate "permissions" directory
    "ServiceRequest": "ferum_customs.permissions.get_service_request_pqc",
}

notification_config = "ferum_customs.notifications.notifications.get_notification_config"

# ─────────────────────────────────────────── fixtures ──────────────────────────────────────────
fixtures = [
    {"dt": "Custom Field"},
    {"dt": "Role", "filters": [["role_name", "in", [
        "Проектный менеджер",
        "Офис-менеджер",
        "Инженер",
        "Заказчик"
    ]]]},
    {"dt": "Custom DocPerm"},
    {"dt": "Workflow", "filters": [["workflow_name", "=", "ServiceRequest Flow"]]},
]

# ────────────────────────────────────────── after_install ──────────────────────────────────────
# after_install = "ferum_customs.after_install.after_install"
