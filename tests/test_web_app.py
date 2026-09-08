"""
Automated Test Suite for SmartBill Web Application
"""
import os
import sys
import unittest

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

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
            cursor.execute("SELECT COUNT(*) FROM users")
            self.assertEqual(cursor.fetchone()[0], 2)
            cursor.execute("SELECT COUNT(*) FROM products")
            self.assertEqual(cursor.fetchone()[0], 12)
            cursor.execute("SELECT name, stock, threshold FROM products WHERE product_code = 'P112'")
            p112 = cursor.fetchone()
            self.assertIsNotNone(p112)
            self.assertLessEqual(p112["stock"], p112["threshold"])

    def test_02_authentication_flows(self):
        res = self.client.post("/login", data={"username": "admin", "password": "wrongpassword"}, follow_redirects=True)
        self.assertIn(b"Invalid username or password", res.data)

        res = self.client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
        self.assertIn(b"Store Dashboard", res.data)
        self.assertIn(b"Admin", res.data)

        res = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Sign In", res.data)

        res = self.client.post("/login", data={"username": "cashier", "password": "cashier123"}, follow_redirects=True)
        self.assertIn(b"Front Desk Cashier", res.data)

    def test_03_product_search_api(self):
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        res = self.client.get("/api/products/search?q=Mouse")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(len(data["products"]), 1)
        self.assertEqual(data["products"][0]["product_code"], "P101")

    def test_04_live_financial_calculation_api(self):
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM products WHERE product_code = 'P101'")
            p101_id = cursor.fetchone()[0]

        payload = {"items": [{"product_id": p101_id, "quantity": 5}]}
        res = self.client.post("/api/calculate", json=payload)
        self.assertEqual(res.status_code, 200)
        fin = res.get_json()
        self.assertEqual(fin["gross_subtotal"], 2495.00)
        self.assertEqual(fin["total_qty_discount"], 124.75)
        self.assertEqual(fin["bill_disc_amt"], 118.51)
        self.assertEqual(fin["total_discount"], 124.75 + 118.51)

    def test_05_checkout_and_inventory_decrement(self):
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, stock FROM products WHERE product_code = 'P101'")
            row = cursor.fetchone()
            p101_id, initial_stock = row[0], row[1]

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

        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT stock FROM products WHERE id = ?", (p101_id,))
            self.assertEqual(cursor.fetchone()[0], initial_stock - 2)

    def test_06_insufficient_stock_rejection(self):
        self.client.post("/login", data={"username": "cashier", "password": "cashier123"})
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, stock FROM products WHERE product_code = 'P112'")
            row = cursor.fetchone()
            p112_id, current_stock = row[0], row[1]

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
        res = self.client.get("/reports")
        self.assertEqual(res.status_code, 200)
        res = self.client.get("/api/chart-data")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sales_trend", data)
        self.assertIn("top_products", data)
        self.assertIn("payment_distribution", data)

if __name__ == "__main__":
    unittest.main()
