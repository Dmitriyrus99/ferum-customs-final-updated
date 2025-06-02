import pytest; pytest.importorskip("frappe")
import frappe
import unittest

class TestServiceObject(unittest.TestCase):
    def test_description_trim(self):
        doc = frappe.new_doc("Service Object")
        doc.linked_service_project = " PROJECT001 "
        doc.validate()
        self.assertEqual(doc.linked_service_project, "PROJECT001")