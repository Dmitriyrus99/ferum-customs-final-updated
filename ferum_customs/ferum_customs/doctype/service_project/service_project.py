# ferum_customs/ferum_customs/doctype/service_project/service_project.py
"""
Python-контроллер для DocType "ServiceProject".
"""
from __future__ import annotations
# from typing import TYPE_CHECKING
import datetime # Для работы с датами и временем

import frappe
from frappe.model.document import Document
from frappe import _

# if TYPE_CHECKING:
    # from .project_object_item import ProjectObjectItem # Для дочерней таблицы
    # pass

class ServiceProject(Document): # Имя класса в CamelCase
    """
    Класс документа ServiceProject.
    """

    def validate(self) -> None:
        """
        Валидация данных документа.
        """
        self._validate_dates()
        self._format_dates_to_iso() # Форматируем после валидации, чтобы валидация работала с объектами дат

        # Логика из оригинального файла (service_project.py):
        # if self.start_date and self.end_date:
        #     if self.end_date < self.start_date:
        #         frappe.throw("Дата окончания проекта меньше даты начала.")
        # if self.start_date:
        #     self.start_date = self.start_date.isoformat()
        # if self.end_date:
        #     self.end_date = self.end_date.isoformat()
        # Эта логика теперь в _validate_dates() и _format_dates_to_iso()


    def _validate_dates(self) -> None:
        """
        Проверяет корректность дат начала и окончания проекта.
        Даты должны быть объектами date/datetime для сравнения.
        """
        # TODO: Verify fieldnames 'start_date', 'end_date' (Date или Datetime)
        start_date_val = self.get("start_date")
        end_date_val = self.get("end_date")

        if start_date_val and end_date_val:
            try:
                # Преобразуем в объекты date/datetime для корректного сравнения
                # Если поля типа Date, get_date() вернет date. Если Datetime, get_datetime() вернет datetime.
                # Для простоты сравнения можно привести все к date, если время не важно.
                # Или использовать get_datetime для обоих, если они Datetime.
                # Предположим, что это поля Date для простоты сравнения дат.
                start_dt = frappe.utils.get_date(start_date_val)
                end_dt = frappe.utils.get_date(end_date_val)

                if end_dt < start_dt:
                    frappe.throw(
                        _("Дата окончания проекта ({0}) не может быть раньше даты начала ({1}).").format(
                            frappe.utils.formatdate(end_dt), frappe.utils.formatdate(start_dt)
                        )
                    )
            except Exception as e:
                # Если даты не удалось распарсить, это может быть ошибкой ввода
                frappe.logger(__name__).warning(
                    f"Could not validate dates for ServiceProject {self.name} due to parsing error: {e}"
                )
                # Можно выбросить ошибку, если формат дат критичен на этом этапе
                # frappe.throw(_("Некорректный формат даты начала или окончания проекта."))


    def _format_dates_to_iso(self) -> None:
        """
        Форматирует поля дат в ISO формат, если они установлены и являются объектами date/datetime.
        """
        date_fields = ["start_date", "end_date"] # TODO: Verify fieldnames
        for fieldname in date_fields:
            field_value = self.get(fieldname)
            if field_value and not isinstance(field_value, str):
                if isinstance(field_value, (datetime.datetime, datetime.date)):
                    try:
                        setattr(self, fieldname, field_value.isoformat())
                    except Exception as e:
                        frappe.logger(__name__).error(f"Error converting date field '{fieldname}' to ISO format for ServiceProject '{self.name}': {e}")
                # else: уже обработано not isinstance(str)
            elif isinstance(field_value, str):
                # Если это уже строка, можно попытаться нормализовать (если нужно).
                # Оригинальный код делал isoformat() без проверки, что вызвало бы ошибку.
                try:
                    dt_obj = frappe.utils.get_datetime(field_value) # или get_date
                    setattr(self, fieldname, dt_obj.date().isoformat() if isinstance(dt_obj, datetime.datetime) else dt_obj.isoformat())
                except Exception:
                     pass # Оставляем как есть, если не парсится или уже в нужном формате


    # Другие методы могут быть добавлены по необходимости.