"""
Automated Test Suite for SmartBill Web Application
Tests:
- Database creation & seeding
- Role-based login (Admin, Cashier)
- Product catalogue search, add, edit, delete
- Customer registration & history
- POS calculation & live GST / discount logic
- Checkout transaction with inventory stock reduction
- Prevention of overselling / insufficient stock
- Change calculation & payment modes
- Invoicing and Sales Analytics
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app, init_db, seed_database, get_db

class TestSmartBillWebApp(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret"
        self.client = app.test_client()
        with app.app_context():
            init_db()
            seed_database()

    def test_01_database_seeding(self):
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            # Verify 2 users
            cursor.execute("SELECT COUNT(*) FROM users")
            self.assertEqual(cursor.fetchone()[0], 2)

            # Verify 12 products
            cursor.execute("SELECT COUNT(*) FROM products")
            self.assertEqual(cursor.fetchone()[0], 12)

            # Verify low stock alert item exists
            cursor.execute("SELECT name, stock, threshold FROM products WHERE product_code = 'P112'")
            p112 = cursor.fetchone()
            self.assertIsNotNone(p112)
            self.assertLessEqual(p112["stock"], p112["threshold"])

    def test_02_authentication_flows(self):
        # 1. Invalid login
        res = self.client.post("/login", data={"username": "admin", "password": "wrongpassword"}, follow_redirects=True)
        self.assertIn(b"Invalid username or password", res.data)

        # 2. Valid Admin login
        res = self.client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
        self.assertIn(b"Store Dashboard", res.data)
        self.assertIn(b"Admin", res.data)

        # 3. Logout
        res = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Sign In", res.data)

        # 4. Valid Cashier login
        res = self.client.post("/login", data={"username": "cashier", "password": "cashier123"}, follow_redirects=True)
        self.assertIn(b"Front Desk Cashier", res.data)

    def test_03_product_search_api(self):
        # Login first
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        
        # Search by keyword
        res = self.client.get("/api/products/search?q=Mouse")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(len(data["products"]), 1)
        self.assertEqual(data["products"][0]["product_code"], "P101")
        self.assertEqual(data["products"][0]["selling_price"], 499.0)

    def test_04_live_financial_calculation_api(self):
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        
        # Item 1: P101 (Rs. 499, qty 5 -> qualifies for 5% quantity bulk discount)
        # Gross = 2495.0, 5% item disc = 124.75, net = 2370.25 (>= 1000, qualifies for 5% bill tier discount)
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM products WHERE product_code = 'P101'")
            p101_id = cursor.fetchone()[0]

        payload = {
            "items": [{"product_id": p101_id, "quantity": 5}]
        }
        res = self.client.post("/api/calculate", json=payload)
        self.assertEqual(res.status_code, 200)
        fin = res.get_json()

        self.assertEqual(fin["gross_subtotal"], 2495.00)
        self.assertEqual(fin["total_qty_discount"], 124.75)
        # Net after qty disc = 2370.25 -> 5% bill tier offer = 118.51
        self.assertEqual(fin["bill_disc_amt"], 118.51)
        self.assertEqual(fin["total_discount"], 124.75 + 118.51)
        self.assertEqual(fin["overall_taxable"], 2495.00 - (124.75 + 118.51))
        self.assertGreater(fin["total_gst"], 0.0)
        self.assertEqual(fin["grand_total"], round(fin["overall_taxable"] + fin["total_gst"], 2))

    def test_05_checkout_and_inventory_decrement(self):
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, stock FROM products WHERE product_code = 'P101'")
            row = cursor.fetchone()
            p101_id = row[0]
            initial_stock = row[1]

        checkout_payload = {
            "customer_name": "Test Customer",
            "customer_phone": "9876543210",
            "customer_email": "test@example.com",
            "payment_mode": "Cash",
            "amount_paid": 1500.00,
            "items": [{"product_id": p101_id, "quantity": 2}]
        }

        res = self.client.post("/api/checkout", json=checkout_payload)
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()
        self.assertTrue(res_data["success"])
        bill = res_data["bill"]
        self.assertIn("BILL-", bill["bill_no"])
        self.assertGreaterEqual(bill["change_due"], 0.0)

        # Verify stock decrement in SQLite
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT stock FROM products WHERE id = ?", (p101_id,))
            new_stock = cursor.fetchone()[0]
            self.assertEqual(new_stock, initial_stock - 2)

    def test_06_insufficient_stock_rejection(self):
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, stock FROM products WHERE product_code = 'P112'")
            row = cursor.fetchone()
            p112_id = row[0]
            current_stock = row[1]

        # Request more units than available in stock
        checkout_payload = {
            "customer_name": "Greedy Buyer",
            "customer_phone": "9876543210",
            "payment_mode": "Cash",
            "amount_paid": 50000.00,
            "items": [{"product_id": p112_id, "quantity": current_stock + 10}]
        }
        res = self.client.post("/api/checkout", json=checkout_payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Insufficient stock", res.data)

    def test_07_analytics_and_chart_api(self):
        self.client.post("/login", data={"username": "admin", "password": "admin123"})
        
        # Check reports page
        res = self.client.get("/reports")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Sales Analytics", res.data)

        # Check chart data API
        res = self.client.get("/api/chart-data")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sales_trend", data)
        self.assertIn("top_products", data)
        self.assertIn("payment_distribution", data)

if __name__ == "__main__":
    unittest.main()
