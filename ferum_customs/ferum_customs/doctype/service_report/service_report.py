# ferum_customs/ferum_customs/doctype/service_report/service_report.py
"""
Python-контроллер для DocType "ServiceReport".
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List 
import datetime 

import frappe
from frappe.model.document import Document
from frappe import _

if TYPE_CHECKING:
    pass

class ServiceReport(Document):
    def onload(self) -> None:
        pass

    def validate(self) -> None:
        self._clean_fields()
        self._validate_work_items() 
        self._set_customer_from_service_request() 
        self.calculate_totals()

    def before_save(self) -> None:
        self.calculate_totals()

    def on_submit(self) -> None:
        pass

    def _clean_fields(self) -> None:
        if self.get("service_request") and isinstance(self.service_request, str):
            self.service_request = self.service_request.strip()

        if self.get("customer") and isinstance(self.customer, str): 
            self.customer = self.customer.strip()

        posting_date_val = self.get("posting_date")
        if posting_date_val:
            if not isinstance(posting_date_val, str): 
                if isinstance(posting_date_val, (datetime.datetime, datetime.date)):
                    self.posting_date = posting_date_val.isoformat()
        else:
             if self.is_new() and self.meta.get_field("posting_date").reqd:
                self.posting_date = frappe.utils.nowdate() 

    def _validate_work_items(self) -> None:
        work_items_table = self.get("work_items")
        if not work_items_table:
            return

        for idx, item in enumerate(work_items_table):
            row_num = idx + 1
            if item.get("description"):
                item.description = item.description.strip()
                if not item.description: 
                    frappe.throw(_("Описание обязательно для всех выполненных работ (строка {0}).").format(row_num))
            else:
                frappe.throw(_("Описание обязательно для всех выполненных работ (строка {0}).").format(row_num))

            if item.get("quantity") is not None and item.quantity < 0:
                frappe.throw(_("Количество не может быть отрицательным (строка {0}).").format(row_num))
            if item.get("unit_price") is not None and item.unit_price < 0:
                frappe.throw(_("Цена за единицу не может быть отрицательной (строка {0}).").format(row_num))

    def _set_customer_from_service_request(self) -> None:
        if self.get("service_request") and not self.get("customer"):
            try:
                customer_from_sr = frappe.db.get_value("ServiceRequest", self.service_request, "custom_customer") # ИЗМЕНЕНО

                if customer_from_sr:
                    self.customer = customer_from_sr 
                else:
                    frappe.logger(__name__).warning(
                        f"Customer not found in linked Service Request '{self.service_request}' (field custom_customer) for ServiceReport '{self.name}'."
                    )
            except Exception as e:
                frappe.logger(__name__).error(
                    f"Error setting customer from ServiceRequest '{self.service_request}' for ServiceReport '{self.name}': {e}",
                    exc_info=True
                )
        elif not self.get("service_request") and self.meta.get_field("customer").read_only == 0:
            pass

    def calculate_totals(self) -> None:
        total_qty: float = 0.0
        total_pay: float = 0.0

        work_items_table: List[Document] = self.get("work_items", []) 

        for item in work_items_table:
            try:
                qty = float(item.get("quantity", 0.0) or 0.0)
                price = float(item.get("unit_price", 0.0) or 0.0)
            except (ValueError, TypeError):
                qty = 0.0
                price = 0.0
                frappe.logger(__name__).warning(
                    f"Invalid numeric value for quantity or unit_price in work_items for SR {self.name}, item idx {item.idx}"
                )

            item.quantity = round(qty, 2)  
            item.unit_price = round(price, 2) 

            amount = round(item.quantity * item.unit_price, 2)
            item.amount = amount 

            total_qty += item.quantity
            total_pay += item.amount

        self.total_quantity = round(total_qty, 2)
        self.total_payable = round(total_pay, 2)