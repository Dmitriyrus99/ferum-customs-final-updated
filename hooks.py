app_name = 'ferum_customs'
app_title = 'Ferum Customizations'
app_publisher = 'Ferum LLC'
app_description = 'Ferum-specific customizations for ERPNext'
app_email = 'support@ferum.ru'
app_license = 'MIT'

app_include_js = "/assets/ferum_customs/js/service_request.js"

# DocEvents
doc_events = {
    "ServiceReport": {
        "on_submit": "ferum_customs.custom_logic.service_report_hooks.update_linked_request_on_submit"
    }
}
