# Ferum Customs - hooks.py fixes
from frappe import _

app_name = "ferum_customs"
app_title = "Ferum Customs"
app_ublisher = "Ferum LLC"
app_description = "Specific custom functionality for ERPNext"
app_email = "support@ferum.ru"
app_license = "MIT"

app_include_js = ["/assets/ferum_customs/js/ferum_customs.js"]

to_populate = []

doc_events = {
    "Service Request": {
        "validate": "ferum_customs.api.validate_service_request",
        "on_submit": "ferum_customs.api.on_submit_service_request",
        "on_cancel": "ferum_customs.api.cancel_service_request"
    },
    "Service Report": {
        "validate": "ferum_customs.api.validate_service_report",
        "on_submit": "ferum_customs.api.on_submit_service_report"
    }
}

get_notification_config = "ferum_customs.config.notifications"

fixtures = [
    "custom_fields",
    "custom_docperm",
    { "dt": "Role", "filters": [["name","in", ["Custom Role"]]] },
    { "dt": "Workflow", "filters": [["name", "in", ["Workflow Service Request"]]]},
    "service_report_workflow",
]