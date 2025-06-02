import pytest; pytest.importorskip("frappe")
import frappe
import unittest

class TestAssignedEngineerItem(unittest.TestCase):
    def test_assignment_date_format(self):
        doc = frappe.new_doc("Assigned Engineer Item")
        doc.engineer = " Engineer User "
        doc.assignment_date = frappe.utils.now_datetime()
        doc.validate()
        self.assertEqual(doc.engineer, "Engineer User")
        self.assertTrue("T" in doc.assignment_date)  # ISO 8601 check