"""
Test suite to automatically verify all core modules of SmartBill.
"""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main

class TestSmartBill(unittest.TestCase):
    def setUp(self):
        main.initialize_data_files()
        self.products = main.load_products()

    def test_sample_products_loaded(self):
        self.assertGreaterEqual(len(self.products), 10)
        p101 = main.find_product_by_id(self.products, "P101")
        self.assertIsNotNone(p101)
        self.assertEqual(p101["name"], "Wireless Optical Mouse")
        self.assertEqual(p101["price"], 499.00)
        self.assertEqual(p101["gst_rate"], 18.0)

    def test_case_insensitive_lookup(self):
        prod_lower = main.find_product_by_id(self.products, "p101")
        prod_upper = main.find_product_by_id(self.products, "P101")
        self.assertEqual(prod_lower, prod_upper)

    def test_item_quantity_discounts(self):
        # < 5 units -> 0%
        rate, amt = main.calculate_item_quantity_discount(100.0, 4)
        self.assertEqual(rate, 0.0)
        self.assertEqual(amt, 0.0)

        # 5 units -> 5%
        rate, amt = main.calculate_item_quantity_discount(100.0, 5)
        self.assertEqual(rate, 5.0)
        self.assertEqual(amt, 25.0)

        # 10 units -> 10%
        rate, amt = main.calculate_item_quantity_discount(100.0, 10)
        self.assertEqual(rate, 10.0)
        self.assertEqual(amt, 100.0)

    def test_bill_tiered_discounts(self):
        # < 1000 -> 0%
        rate, amt = main.calculate_bill_tier_discount(999.0)
        self.assertEqual(rate, 0.0)
        self.assertEqual(amt, 0.0)

        # >= 1000 -> 5%
        rate, amt = main.calculate_bill_tier_discount(1500.0)
        self.assertEqual(rate, 5.0)
        self.assertEqual(amt, 75.0)

        # >= 3000 -> 10%
        rate, amt = main.calculate_bill_tier_discount(3500.0)
        self.assertEqual(rate, 10.0)
        self.assertEqual(amt, 350.0)

        # >= 5000 -> 15%
        rate, amt = main.calculate_bill_tier_discount(6000.0)
        self.assertEqual(rate, 15.0)
        self.assertEqual(amt, 900.0)

    def test_cart_financials_and_gst(self):
        sample_cart = [
            {
                "id": "P101",
                "name": "Wireless Optical Mouse",
                "category": "Electronics",
                "price": 499.00,
                "qty": 2,
                "gst_rate": 18.0,
                "threshold": 5
            },
            {
                "id": "P106",
                "name": "Royal Basmati Rice (5 kg)",
                "category": "Groceries",
                "price": 450.00,
                "qty": 1,
                "gst_rate": 5.0,
                "threshold": 5
            }
        ]
        fin = main.compute_bill_financials(sample_cart)
        # Gross = (499 * 2) + (450 * 1) = 998 + 450 = 1448.00
        self.assertEqual(fin["gross_subtotal"], 1448.00)
        # Bill discount >= 1000 is 5% -> 1448 * 0.05 = 72.40
        self.assertEqual(fin["bill_disc_amt"], 72.40)
        self.assertEqual(fin["overall_taxable"], 1375.60)
        # Grand total = taxable + total_gst
        self.assertEqual(fin["grand_total"], round(fin["overall_taxable"] + fin["total_gst"], 2))

    def test_stock_deduction_and_persistence(self):
        p101 = main.find_product_by_id(self.products, "P101")
        initial_stock = p101["stock"]
        
        # Deduct 2 units
        p101["stock"] -= 2
        main.save_products(self.products)

        # Reload and check
        fresh_products = main.load_products()
        fresh_p101 = main.find_product_by_id(fresh_products, "P101")
        self.assertEqual(fresh_p101["stock"], initial_stock - 2)

        # Restore
        fresh_p101["stock"] = initial_stock
        main.save_products(fresh_products)

if __name__ == "__main__":
    unittest.main()
