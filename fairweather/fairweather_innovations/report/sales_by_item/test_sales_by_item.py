# Copyright (c) 2021, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

import unittest

filters = {
    "from_date": "2019-01-01",
    "to_date": "2019-01-31",
    "item_group": "All Item Groups",
    "customer": "All Customers",
}


class TestSalesByItem(unittest.TestCase):
    def test_get_conditions(self):
        """Tests get conditions"""
        global filters

        conditions = get_conditions(filters)

        self.assertTrue("from_date" in conditions)
        self.assertTrue("to_date" in conditions)


if __name__ == '__main__':
    unittest.main()
