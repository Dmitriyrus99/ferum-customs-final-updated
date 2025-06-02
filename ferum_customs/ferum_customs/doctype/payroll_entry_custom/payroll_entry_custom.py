# ferum_customs/ferum_customs/doctype/payroll_entry_custom/payroll_entry_custom.py
"""
Python-контроллер для DocType "PayrollEntryCustom".
"""
from __future__ import annotations
# from typing import TYPE_CHECKING

# import frappe # Не используется напрямую в этом файле, кроме как для frappe.model.document.Document
from frappe.model.document import Document
# from frappe import _ # Если будут пользовательские сообщения

# if TYPE_CHECKING:
    # pass

class PayrollEntryCustom(Document):
    """
    Класс документа PayrollEntryCustom.
    """

    def validate(self) -> None:
        """
        Валидация данных документа.
        Проверка дат (start_date, end_date) вынесена в
        `custom_logic.payroll_entry_hooks.validate`.
        Расчет `total_payable` вынесен в
        `custom_logic.payroll_entry_hooks.before_save`.
        Здесь можно добавить специфичные для класса валидации.
        """
        self._round_total_payable()
        
        # Логика из оригинального файла (payroll_entry_custom.py):
        # if self.total_payable is not None:
        #     self.total_payable = round(float(self.total_payable), 2)
        # Эта логика теперь в _round_total_payable()

    def _round_total_payable(self) -> None:
        """
        Округляет поле `total_payable` до двух знаков после запятой, если оно установлено и является числом.
        """
        # TODO: Verify fieldname 'total_payable'
        if self.get("total_payable") is not None:
            try:
                # Преобразуем в float перед округлением, на случай если это строка или Decimal
                payable_float = float(self.total_payable)
                self.total_payable = round(payable_float, 2)
            except (ValueError, TypeError):
                # Если значение не может быть преобразовано в float, логируем или выбрасываем ошибку.
                # В данном случае, просто не изменяем значение, если оно не числовое.
                # Это может быть обработано другими валидациями (например, тип поля Currency).
                pass # Или frappe.log_error(...)
    
    # Другие методы жизненного цикла (before_save, on_submit, etc.) могут быть добавлены по необходимости.
    # before_save: Логика расчета total_payable находится в custom_logic.payroll_entry_hooks.before_save