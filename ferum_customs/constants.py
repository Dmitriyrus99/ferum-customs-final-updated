"""Единый набор констант, используемых во всём приложении.

Содержит как англоязычные (наследие ERPNext), так и русскоязычные
идентификаторы статусов и ролей ‒ для удобства локализованной логики.
"""

# --- Англоязычные статусы (оставлены для обратной совместимости) ---
STATUS_OPEN: str = "Open"
STATUS_WORKING: str = "Working"
STATUS_COMPLETED: str = "Completed"
STATUS_CLOSED: str = "Closed"
STATUS_CANCELLED: str = "Cancelled"

# --- Русскоязычные статусы (основные в приложении) ---
STATUS_OTKRYTA: str = "Открыта"
STATUS_V_RABOTE: str = "В работе"
STATUS_VYPOLNENA: str = "Выполнена"
STATUS_ZAKRYTA: str = "Закрыта"
STATUS_OTMENENA: str = "Отменена"

# --- Роли ---
ROLE_ADMIN: str = "Administrator"
ROLE_PROEKTNYJ_MENEDZHER: str = "Проектный менеджер"
ROLE_INZHENER: str = "Инженер"
ROLE_ZAKAZCHIK: str = "Заказчик"
ROLE_OFIS_MENEDZHER: str = "Офис-менеджер"

__all__ = [  # «экспортируемый» публичный интерфейс
    k for k in globals() if k.startswith(("STATUS_", "ROLE_"))
]
