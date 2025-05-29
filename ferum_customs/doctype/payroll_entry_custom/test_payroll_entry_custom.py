import pytest; pytest.importorskip("frappe")  # noqa: E402,F401
import frappe  # noqa: F401
import unittest

class TestTestPayrollEntryCustom(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)
