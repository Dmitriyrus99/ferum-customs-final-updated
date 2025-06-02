import pytest; pytest.importorskip("frappe")
import frappe
import unittest

class TestPayrollEntryCustom(unittest.TestCase):
    def test_total_payable_rounding(self):
        doc = frappe.new_doc("Payroll Entry Custom")
        doc.total_payable = 1234.567
        doc.validate()
        self.assertAlmostEqual(doc.total_payable, 1234.57, places=2)