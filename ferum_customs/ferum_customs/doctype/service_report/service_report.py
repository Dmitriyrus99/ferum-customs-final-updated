# ferum_customs/ferum_customs/doctype/ServiceReport/service_report.py
# ... other imports
import frappe
from frappe.model.document import Document

class ServiceReport(Document):
    def validate(self) -> None:
        self.validate_work_items_description()
        self.set_customer_from_service_request()
        self.calculate_totals()

    def before_save(self) -> None:
        self.calculate_totals()

    def validate_work_items_description(self) -> None:
        for item in self.get("work_items"):
            if not item.description:
                frappe.throw(frappe._('Description is mandatory for all work items.'))

    def set_customer_from_service_request(self) -> None:
        if self.service_request and not self.customer:
            customer = frappe.db.get_value("service_request", self.service_request, "customer")
            if customer:
                self.customer = customer
            else:
                frappe.throw(frappe._("Customer not found in linked Service Request {0}.").format(self.service_request))
        elif not self.service_request:
             frappe.throw(frappe._("Service Request is mandatory to link a customer."))


    def calculate_totals(self) -> None:
        """Calculates total quantity and total payable from work items."""
        total_qty = 0.0
        total_pay = 0.0
        for item in self.get("work_items", []):
            item.amount = (item.quantity or 0) * (item.unit_price or 0)
            total_qty += item.quantity or 0
            total_pay += item.amount or 0
        
        self.total_quantity = total_qty
        self.total_payable = total_pay

    # ... (any existing methods)