# ferum_customs/ferum_customs/doctype/service_request/service_request.py
"""
Python-контроллер для DocType "ServiceRequest".
"""
from __future__ import annotations
from typing import TYPE_CHECKING 
import datetime 

import frappe
from frappe.model.document import Document
from frappe import _ 

# from ...constants import STATUS_OTKRYTA, STATUS_V_RABOTE # Пример

if TYPE_CHECKING:
    pass


class ServiceRequest(Document):
    def onload(self) -> None:
        pass

    def validate(self) -> None:
        self._clean_fields()
        self._validate_dates()

        # Пример: Клиент обязателен, если указан проект
        # Эта логика также есть в service_request_hooks.py. Не дублируйте без необходимости.
        # Если дублируете, убедитесь в согласованности.
        if self.get("custom_project") and not self.get("custom_customer"): # ИЗМЕНЕНО x2
            customer_from_project = frappe.db.get_value("ServiceProject", self.custom_project, "customer") # ИЗМЕНЕНО
            if customer_from_project:
                self.custom_customer = customer_from_project # ИЗМЕНEНО
            # else:
                # frappe.throw(_("Клиент должен быть указан (контроллер SR)."))

    def before_save(self) -> None:
        self._calculate_duration()

        if self.get("custom_service_object_link") and not self.get("custom_project"): # ИЗМЕНЕНО x2
            linked_project = frappe.db.get_value("ServiceObject", self.custom_service_object_link, "linked_service_project") # ИЗМЕНЕНО
            if linked_project:
                self.custom_project = linked_project # ИЗМЕНЕНО

    def on_submit(self) -> None:
        if not self.get("actual_start_datetime"):
             # if self.status == STATUS_V_RABOTE: # Учитывайте статус
             self.db_set("actual_start_datetime", frappe.utils.now_datetime())
             # frappe.msgprint(_("Фактическое время начала работ установлено: {0}").format(
             # frappe.utils.format_datetime(self.actual_start_datetime)
             # ))
        pass

    def on_update(self) -> None:
        pass

    def on_cancel(self) -> None:
        # if self.get("custom_assigned_engineer"): # ИЗМЕНЕНО
        #     self.db_set("custom_assigned_engineer", None) # ИЗМЕНЕНО
        pass

    def on_trash(self) -> None:
        pass

    def _clean_fields(self) -> None:
        if self.get("subject") and isinstance(self.subject, str):
            self.subject = self.subject.strip()

        # Для полей Link .strip() обычно не нужен.
        # if self.get("custom_customer") and isinstance(self.custom_customer, str): # ИЗМЕНЕНО
        #     self.custom_customer = self.custom_customer.strip() # ИЗМЕНЕНО

        datetime_fields = [
            "request_datetime", "completed_on", 
            "planned_start_datetime", "planned_end_datetime",
            "actual_start_datetime", "actual_end_datetime"
        ] 

        for fieldname in datetime_fields:
            field_value = self.get(fieldname)
            if field_value:
                if isinstance(field_value, str):
                    try:
                        dt_obj = frappe.utils.get_datetime(field_value)
                        setattr(self, fieldname, dt_obj.isoformat())
                    except ValueError:
                        frappe.logger(__name__).warning(f"Could not parse datetime string for field '{fieldname}' ('{field_value}') in SR '{self.name}'.")
                elif isinstance(field_value, datetime.datetime):
                    setattr(self, fieldname, field_value.isoformat())
                elif isinstance(field_value, datetime.date):
                     setattr(self, fieldname, field_value.isoformat())

    def _validate_dates(self) -> None:
        date_pairs_to_validate = [
            ("planned_start_datetime", "planned_end_datetime", _("Планируемая дата начала работ не может быть позже планируемой даты окончания.")),
            ("actual_start_datetime", "actual_end_datetime", _("Фактическая дата начала работ не может быть позже фактической даты окончания."))
        ]

        for start_field, end_field, error_message in date_pairs_to_validate:
            start_val = self.get(start_field)
            end_val = self.get(end_field)

            if start_val and end_val:
                try:
                    start_dt = frappe.utils.get_datetime(start_val)
                    end_dt = frappe.utils.get_datetime(end_val)
                    if start_dt > end_dt:
                        frappe.throw(error_message)
                except ValueError:
                    frappe.throw(_("Некорректный формат даты для полей {0} или {1}.").format(start_field, end_field))

    def _calculate_duration(self) -> None:
        if self.get("actual_start_datetime") and self.get("actual_end_datetime"):
            try:
                start_dt = frappe.utils.get_datetime(self.actual_start_datetime)
                end_dt = frappe.utils.get_datetime(self.actual_end_datetime)

                if end_dt >= start_dt:
                    duration_timedelta = end_dt - start_dt
                    duration_in_hours = duration_timedelta.total_seconds() / 3600.0
                    self.duration_hours = round(duration_in_hours, 2)
                else:
                    self.duration_hours = 0.0 
            except Exception as e:
                frappe.logger(__name__).warning(
                    f"Could not calculate duration for SR {self.name}: {e}"
                )
                self.duration_hours = None 
        elif self.get("duration_hours") is not None:
            try:
                self.duration_hours = round(float(self.duration_hours), 2)
            except (ValueError, TypeError):
                 self.duration_hours = None