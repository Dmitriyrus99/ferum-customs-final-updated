def get_notification_config():
    return {
        'for_doctype': {
            'service_request': {
                'status': ['Открыта', 'В работе']
            }
        }
    }
