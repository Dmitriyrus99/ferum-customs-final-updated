import pytest; pytest.importorskip("frappe")
import frappe
import unittest

class TestCustomAttachment(unittest.TestCase):
    def test_basic(self):
        doc = frappe.new_doc("Custom Attachment")
        doc.attachment_type = " Photo "
        doc.attachment_file = " /path/to/file.jpg "
        doc.validate()
        self.assertEqual(doc.attachment_type, "photo")
        self.assertEqual(doc.attachment_file, "/path/to/file.jpg")