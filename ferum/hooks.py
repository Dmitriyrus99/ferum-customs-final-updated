
# Hook for attachment deletion
doc_events = {
    "File": {
        "on_trash": "custom_logic.attachment_hooks.delete_attachment_file"
    }
}
