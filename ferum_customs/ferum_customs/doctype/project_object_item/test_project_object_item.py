import pytest; pytest.importorskip("frappe")
import frappe
import unittest

class TestProjectObjectItem(unittest.TestCase):
    def test_description_trim(self):
        doc = frappe.new_doc("Project Object Item")
        doc.description = " Test description "
        doc.validate()
        self.assertEqual(doc.description, "Test description")