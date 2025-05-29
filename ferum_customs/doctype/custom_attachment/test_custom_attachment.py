import pytest; pytest.importorskip("frappe")  # noqa: E402,F401
import frappe
import unittest

class TestCustomAttachment(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)
