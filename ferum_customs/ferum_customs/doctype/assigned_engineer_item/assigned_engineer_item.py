# ferum_customs/ferum_customs/doctype/assigned_engineer_item/assigned_engineer_item.py
"""
Python-контроллер для дочернего DocType "AssignedEngineerItem".
Этот DocType, вероятно, используется как таблица в другом документе (например, ServiceObject).
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import datetime # Для работы с датами и временем

import frappe
from frappe.model.document import Document
from frappe import _ # Для возможных пользовательских сообщений

if TYPE_CHECKING:
    # from frappe.types import DF # Для типов полей DocField
    # from ...user.user import User # Если ссылка на User
    pass

class AssignedEngineerItem(Document): # Имя класса должно совпадать с именем DocType, но в CamelCase
    """
    Класс документа (дочерней таблицы) AssignedEngineerItem.
    """

    def validate(self) -> None:
        """
        Валидация данных для строки дочерней таблицы.
        """
        self._clean_engineer_field()
        self._format_assignment_date()

        # Логика из оригинального файла (assigned_engineer_item.py):
        # if self.engineer:
        #     self.engineer = self.engineer.strip()
        # if self.assignment_date:
        #     self.assignment_date = self.assignment_date.isoformat() # Это может быть проблематично, если assignment_date уже строка
        # Эта логика теперь в _clean_engineer_field() и _format_assignment_date()


    def _clean_engineer_field(self) -> None:
        """
        Очищает поле инженера.
        """
        # TODO: Verify fieldname 'engineer' (Link to User)
        # Поле 'engineer' - это Link на User. ID пользователя обычно не содержит пробелов.
        # .strip() здесь, вероятно, излишен, если только это не Data поле по какой-то причине.
        if self.get("engineer") and isinstance(self.engineer, str):
            original_value = self.engineer
            self.engineer = self.engineer.strip()
            if self.engineer != original_value:
                 frappe.logger(__name__).debug(f"Stripped whitespace from 'engineer' field in AssignedEngineerItem (parent: {self.parent}), original: '{original_value}', new: '{self.engineer}'")


    def _format_assignment_date(self) -> None:
        """
        Форматирует дату назначения в ISO формат.
        """
        # TODO: Verify fieldname 'assignment_date' (Datetime field)
        assignment_date_val = self.get("assignment_date")
        if assignment_date_val:
            if not isinstance(assignment_date_val, str): # Если это объект datetime
                if isinstance(assignment_date_val, datetime.datetime):
                    try:
                        self.assignment_date = assignment_date_val.isoformat()
                    except Exception as e:
                        frappe.logger(__name__).error(f"Error converting datetime field 'assignment_date' to ISO format for AssignedEngineerItem (parent: {self.parent}): {e}")
                elif isinstance(assignment_date_val, datetime.date): # На случай, если это Date, а не DateTime
                     self.assignment_date = assignment_date_val.isoformat()
            else:
                # Если это уже строка, можно попытаться распарсить и переформатировать для консистентности,
                # но это может быть избыточно и привести к ошибкам, если формат строки неожиданный.
                # Frappe обычно сам обрабатывает строки дат при сохранении.
                # Оригинальный код делал .isoformat() без проверки типа, что вызвало бы ошибку, если это уже строка.
                try:
                    # Попытка распарсить, если это строка, и переформатировать.
                    # Это нужно, только если есть вероятность, что дата приходит в не-ISO строковом формате.
                    dt_obj = frappe.utils.get_datetime(assignment_date_val)
                    self.assignment_date = dt_obj.isoformat()
                except (ValueError, TypeError):
                    # Если строка не парсится, оставляем как есть, или логируем/выбрасываем ошибку.
                    frappe.logger(__name__).warning(
                        f"Could not parse or re-format 'assignment_date' string '{assignment_date_val}' in AssignedEngineerItem (parent: {self.parent})."
                    )
                    # Можно добавить frappe.throw, если требуется строгий ISO формат.
                    # frappe.throw(_("Некорректный формат даты назначения: {0}").format(assignment_date_val))


    # Другие методы (before_save_row, after_save_row и т.д.) можно добавить по необходимости.