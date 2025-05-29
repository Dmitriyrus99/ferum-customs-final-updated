def get_notification_config():
    return {
        'for_doctype': {
            'ServiceRequest': {
                'status': ['Открыта', 'В работе']
            }
        }
    }
