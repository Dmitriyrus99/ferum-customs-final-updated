import pytest; pytest.importorskip("frappe")
import frappe
import unittest

class TestServiceProject(unittest.TestCase):
    def test_date_validation(self):
        doc = frappe.new_doc("Service Project")
        doc.start_date = frappe.utils.now_datetime()
        doc.end_date = frappe.utils.add_days(doc.start_date, -1)
        with self.assertRaises(frappe.ValidationError):
            doc.validate()