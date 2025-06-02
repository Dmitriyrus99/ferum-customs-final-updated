import pytest; pytest.importorskip("frappe")
import frappe
import unittest
import re

class TestServiceReport(unittest.TestCase):
    def test_basic(self):
        doc = frappe.new_doc("Service Report")
        doc.service_request = " TEST123 "
        doc.customer = " CUSTOMER1 "
        doc.posting_date = frappe.utils.now_datetime()
        doc.append("work_items", {
            "description": " Test work item ",
            "quantity": 2.555,
            "unit_price": 100.555
        })
        doc.validate()
        self.assertTrue(doc.posting_date.endswith('Z') or re.match(r".*\+\d{2}:\d{2}", doc.posting_date))
        for item in doc.work_items:
            self.assertEqual(item.description, "Test work item")
            self.assertAlmostEqual(item.quantity, 2.56, places=2)
            self.assertAlmostEqual(item.unit_price, 100.56, places=2)
            self.assertAlmostEqual(item.amount, 257.43, places=2)