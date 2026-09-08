"""
================================================================================
SmartBill – Smart Billing & Inventory Management System (Web Application)
================================================================================
A modern, responsive, full-stack retail billing and inventory management
web application developed using Python, Flask, and SQLite.

Author: B.Tech CSE Student
Stack: Python 3, Flask, SQLite3, HTML5, CSS3, JavaScript, Chart.js
================================================================================
"""

import os
import sqlite3
import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------------------------------------------------------------------
# APPLICATION CONFIGURATION
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "smartbill-retail-pos-secret-key-2026"
app.config["DATABASE"] = DATABASE

# ------------------------------------------------------------------------------
# DATABASE CONNECTION & UTILITIES
# ------------------------------------------------------------------------------
def get_db():
    """Open a unique database connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        # Enable foreign key constraints in SQLite
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all required tables in SQLite database if they do not exist."""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # 1. Users table (Admin & Cashier)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Admin', 'Cashier')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Products table (with Cost Price for profit estimation)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            cost_price REAL NOT NULL CHECK(cost_price >= 0),
            selling_price REAL NOT NULL CHECK(selling_price >= 0),
            stock INTEGER NOT NULL CHECK(stock >= 0),
            threshold INTEGER NOT NULL DEFAULT 5 CHECK(threshold >= 0),
            gst_rate REAL NOT NULL DEFAULT 18.0 CHECK(gst_rate >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            email TEXT,
            total_purchases REAL DEFAULT 0.0,
            bill_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Bills table (Invoices)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no TEXT UNIQUE NOT NULL,
            customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            bill_date TEXT NOT NULL,
            bill_time TEXT NOT NULL,
            subtotal REAL NOT NULL,
            discount REAL NOT NULL,
            taxable_amount REAL NOT NULL,
            total_gst REAL NOT NULL,
            grand_total REAL NOT NULL,
            payment_mode TEXT NOT NULL CHECK(payment_mode IN ('Cash', 'UPI', 'Card')),
            amount_paid REAL NOT NULL,
            change_due REAL NOT NULL DEFAULT 0.0,
            payment_ref TEXT,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Bill items table (Line items)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            product_code TEXT NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            subtotal REAL NOT NULL,
            item_discount REAL NOT NULL DEFAULT 0.0,
            taxable_amount REAL NOT NULL,
            gst_rate REAL NOT NULL,
            gst_amount REAL NOT NULL,
            item_total REAL NOT NULL
        )
    """)

    db.commit()
    db.close()


def seed_database():
    """Seed initial sample users and products if database is newly created."""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # Seed Default Users if none exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass = generate_password_hash("admin123")
        cashier_pass = generate_password_hash("cashier123")

        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?), (?, ?, ?, ?)
        """, (
            "admin", admin_pass, "Store Administrator", "Admin",
            "cashier", cashier_pass, "Front Desk Cashier", "Cashier"
        ))

    # Seed 12 Diverse Retail Products if none exist
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("P101", "Wireless Optical Mouse", "Electronics", 320.0, 499.0, 25, 5, 18.0),
            ("P102", "Mechanical Gaming Keyboard", "Electronics", 1250.0, 1899.0, 15, 3, 18.0),
            ("P103", "USB-C Fast Cable (1.5m)", "Electronics", 110.0, 249.0, 40, 8, 18.0),
            ("P104", "Bluetooth Over-Ear Headphones", "Electronics", 950.0, 1499.0, 18, 4, 18.0),
            ("P105", "10000mAh Slim Power Bank", "Electronics", 650.0, 999.0, 20, 5, 18.0),
            ("P106", "A4 Spiral Ruled Notebook (200p)", "Stationery", 45.0, 85.0, 50, 10, 12.0),
            ("P107", "Premium Gel Pen Set (5 pcs)", "Stationery", 70.0, 120.0, 30, 6, 12.0),
            ("P108", "Scientific Pocket Calculator", "Stationery", 380.0, 550.0, 15, 3, 18.0),
            ("P109", "Insulated Stainless Bottle (750ml)", "Lifestyle", 280.0, 450.0, 22, 5, 18.0),
            ("P110", "Ergonomic Laptop Backpack", "Lifestyle", 650.0, 1199.0, 12, 3, 18.0),
            ("P111", "Royal Basmati Rice (5 kg)", "Groceries", 360.0, 450.0, 20, 5, 5.0),
            ("P112", "Herbal Aloe Hand Sanitizer (500ml)", "Personal Care", 65.0, 110.0, 4, 5, 18.0),  # Low stock test
        ]
        cursor.executemany("""
            INSERT INTO products (product_code, name, category, cost_price, selling_price, stock, threshold, gst_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_products)

    # Seed Sample Customers if none exist
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ("Priya Sharma", "9876543210", "priya.sharma@example.com", 0.0, 0),
            ("Rahul Verma", "9123456780", "rahul.v@example.com", 0.0, 0),
            ("Ananya Iyer", "9988776655", "ananya.iyer@example.com", 0.0, 0)
        ]
        cursor.executemany("""
            INSERT INTO customers (name, phone, email, total_purchases, bill_count)
            VALUES (?, ?, ?, ?, ?)
        """, sample_customers)

    db.commit()
    db.close()


# Initialize database and seeds on startup
init_db()
seed_database()


# ------------------------------------------------------------------------------
# AUTHENTICATION & ACCESS CONTROL HELPERS
# ------------------------------------------------------------------------------
def login_required(f):
    """Decorator requiring an active authenticated user session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access the SmartBill system.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator restricting route access exclusively to Admin users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("user_role") != "Admin":
            flash("Access denied! This operation requires Administrator privileges.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------------------
# BUSINESS LOGIC: DISCOUNTS & GST CALCULATIONS
# ------------------------------------------------------------------------------
def calculate_bill_financials(cart_items):
    """
    Given a list of cart item dicts:
    [{'id': ..., 'code': ..., 'name': ..., 'category': ..., 'cost_price': ...,
      'selling_price': ..., 'gst_rate': ..., 'quantity': ...}]

    Calculates:
    1. Item-level quantity bulk discount (5% for 5-9 units, 10% for 10+ units)
    2. Net subtotal
    3. Bill-level tiered discount:
       - Subtotal >= Rs. 10,000 : 15%
       - Subtotal >= Rs. 5,000  : 10%
       - Subtotal >= Rs. 1,000  : 5%
       - Below Rs. 1,000        : 0%
    4. Proportional distribution of bill discount across items
    5. GST calculation per item on its net taxable value
    6. Overall taxable value, total GST, and Grand Total
    """
    gross_subtotal = 0.0
    total_qty_discount = 0.0
    item_lines = []

    for item in cart_items:
        price = float(item["selling_price"])
        qty = int(item["quantity"])
        line_gross = round(price * qty, 2)

        # Quantity bulk discount
        if qty >= 10:
            qty_rate = 10.0
        elif qty >= 5:
            qty_rate = 5.0
        else:
            qty_rate = 0.0

        qty_disc_amt = round(line_gross * (qty_rate / 100.0), 2)
        line_after_qty = line_gross - qty_disc_amt

        gross_subtotal += line_gross
        total_qty_discount += qty_disc_amt

        item_lines.append({
            "product_id": item["id"],
            "product_code": item.get("product_code", ""),
            "name": item["name"],
            "category": item["category"],
            "cost_price": float(item.get("cost_price", 0.0)),
            "selling_price": price,
            "quantity": qty,
            "line_gross": line_gross,
            "qty_disc_rate": qty_rate,
            "qty_disc_amt": qty_disc_amt,
            "line_after_qty": line_after_qty,
            "gst_rate": float(item["gst_rate"])
        })

    net_after_qty_disc = gross_subtotal - total_qty_discount

    # Bill-level tiered store offer
    if net_after_qty_disc >= 10000:
        bill_disc_rate = 15.0
    elif net_after_qty_disc >= 5000:
        bill_disc_rate = 10.0
    elif net_after_qty_disc >= 1000:
        bill_disc_rate = 5.0
    else:
        bill_disc_rate = 0.0

    bill_disc_amt = round(net_after_qty_disc * (bill_disc_rate / 100.0), 2)
    total_discount = round(total_qty_discount + bill_disc_amt, 2)
    overall_taxable = round(gross_subtotal - total_discount, 2)

    # Distribute bill discount proportionally to calculate exact GST per item
    total_gst = 0.0
    processed_items = []

    for line in item_lines:
        if net_after_qty_disc > 0:
            prop_bill_disc = round(bill_disc_amt * (line["line_after_qty"] / net_after_qty_disc), 2)
        else:
            prop_bill_disc = 0.0

        item_taxable = max(0.0, round(line["line_after_qty"] - prop_bill_disc, 2))
        item_gst = round(item_taxable * (line["gst_rate"] / 100.0), 2)
        item_final = round(item_taxable + item_gst, 2)

        total_gst += item_gst

        processed_items.append({
            "product_id": line["product_id"],
            "product_code": line["product_code"],
            "product_name": line["name"],
            "category": line["category"],
            "cost_price": line["cost_price"],
            "selling_price": line["selling_price"],
            "quantity": line["quantity"],
            "subtotal": line["line_gross"],
            "item_discount": round(line["qty_disc_amt"] + prop_bill_disc, 2),
            "taxable_amount": item_taxable,
            "gst_rate": line["gst_rate"],
            "gst_amount": item_gst,
            "item_total": item_final
        })

    total_gst = round(total_gst, 2)
    grand_total = round(overall_taxable + total_gst, 2)

    return {
        "gross_subtotal": round(gross_subtotal, 2),
        "total_qty_discount": round(total_qty_discount, 2),
        "bill_disc_rate": bill_disc_rate,
        "bill_disc_amt": round(bill_disc_amt, 2),
        "total_discount": total_discount,
        "overall_taxable": overall_taxable,
        "total_gst": total_gst,
        "grand_total": grand_total,
        "items": processed_items
    }


def generate_unique_bill_no(db):
    """Generate sequential invoice number: BILL-YYYYMMDD-XXXX."""
    today_str = datetime.date.today().strftime("%Y%m%d")
    prefix = f"BILL-{today_str}-%"
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM bills WHERE bill_no LIKE ?", (prefix,))
    count_today = cursor.fetchone()[0]
    return f"BILL-{today_str}-{(count_today + 1):04d}"


# ------------------------------------------------------------------------------
# AUTHENTICATION ROUTES
# ------------------------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["user_role"] = user["role"]
            flash(f"Welcome back, {user['full_name']}! Signed in as {user['role']}.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("login"))


# ------------------------------------------------------------------------------
# DASHBOARD ROUTE
# ------------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()

    today_str = datetime.date.today().strftime("%d/%m/%Y")

    # 1. Today's Sales Revenue
    cursor.execute("SELECT SUM(grand_total) FROM bills WHERE bill_date = ?", (today_str,))
    today_sales = cursor.fetchone()[0] or 0.0

    # 2. Total Invoices Generated
    cursor.execute("SELECT COUNT(*) FROM bills")
    total_bills = cursor.fetchone()[0]

    # 3. Total Unique Products in Catalogue
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # 4. Low Stock Products Count (stock <= threshold)
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= threshold")
    low_stock_count = cursor.fetchone()[0]

    # 5. Total Customers Count
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]

    # 6. Total GST Collected All-Time
    cursor.execute("SELECT SUM(total_gst) FROM bills")
    total_gst = cursor.fetchone()[0] or 0.0

    # 7. Recent Invoices (Latest 5)
    cursor.execute("""
        SELECT b.*, u.full_name as cashier_name
        FROM bills b
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY b.id DESC LIMIT 5
    """)
    recent_bills = cursor.fetchall()

    # 8. Low Stock Alert Items (Products where stock <= threshold)
    cursor.execute("""
        SELECT * FROM products
        WHERE stock <= threshold
        ORDER BY stock ASC LIMIT 6
    """)
    low_stock_items = cursor.fetchall()

    # 9. Top 5 Selling Products
    cursor.execute("""
        SELECT product_name, category, SUM(quantity) as units_sold, SUM(item_total) as total_rev
        FROM bill_items
        GROUP BY product_id
        ORDER BY units_sold DESC LIMIT 5
    """)
    top_products = cursor.fetchall()

    stats = {
        "today_sales": today_sales,
        "total_bills": total_bills,
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "total_customers": total_customers,
        "total_gst": total_gst
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_bills=recent_bills,
        low_stock_items=low_stock_items,
        top_products=top_products
    )


# ------------------------------------------------------------------------------
# POS BILLING TERMINAL & APIS
# ------------------------------------------------------------------------------
@app.route("/billing")
@login_required
def billing():
    db = get_db()
    cursor = db.cursor()
    # Fetch distinct categories for quick filtering
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]
    return render_template("billing.html", categories=categories)


@app.route("/api/products/search")
@login_required
def api_product_search():
    """Real-time product search by code, name, or category."""
    query = request.args.get("q", "").strip()
    category = request.args.get("cat", "").strip()

    db = get_db()
    cursor = db.cursor()

    sql = "SELECT * FROM products WHERE stock > 0"
    params = []

    if query:
        sql += " AND (product_code LIKE ? OR name LIKE ? OR category LIKE ?)"
        term = f"%{query}%"
        params.extend([term, term, term])

    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY name ASC LIMIT 25"
    cursor.execute(sql, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "product_code": r["product_code"],
            "name": r["name"],
            "category": r["category"],
            "cost_price": r["cost_price"],
            "selling_price": r["selling_price"],
            "stock": r["stock"],
            "threshold": r["threshold"],
            "gst_rate": r["gst_rate"]
        })

    return jsonify({"products": results})


@app.route("/api/calculate", methods=["POST"])
@login_required
def api_calculate():
    """Live computation of cart financial totals, discounts, and GST."""
    data = request.get_json() or {}
    items = data.get("items", [])

    if not items:
        return jsonify({
            "gross_subtotal": 0.0,
            "total_discount": 0.0,
            "overall_taxable": 0.0,
            "total_gst": 0.0,
            "grand_total": 0.0,
            "items": []
        })

    db = get_db()
    cursor = db.cursor()

    hydrated_cart = []
    for itm in items:
        p_id = itm.get("product_id")
        qty = int(itm.get("quantity", 1))

        cursor.execute("SELECT * FROM products WHERE id = ?", (p_id,))
        prod = cursor.fetchone()
        if prod:
            hydrated_cart.append({
                "id": prod["id"],
                "product_code": prod["product_code"],
                "name": prod["name"],
                "category": prod["category"],
                "cost_price": prod["cost_price"],
                "selling_price": prod["selling_price"],
                "gst_rate": prod["gst_rate"],
                "quantity": qty
            })

    financials = calculate_bill_financials(hydrated_cart)
    return jsonify(financials)


@app.route("/api/checkout", methods=["POST"])
@login_required
def api_checkout():
    """Complete billing transaction, deduct stock, persist invoice, and return receipt."""
    data = request.get_json() or {}

    customer_name = data.get("customer_name", "").strip()
    customer_phone = data.get("customer_phone", "").strip()
    customer_email = data.get("customer_email", "").strip()
    payment_mode = data.get("payment_mode", "Cash")
    amount_paid = float(data.get("amount_paid", 0.0))
    payment_ref = data.get("payment_ref", "").strip()
    cart_items = data.get("items", [])

    # Validations
    if not customer_name:
        return jsonify({"success": False, "error": "Customer name is required."}), 400

    phone_clean = customer_phone.replace(" ", "").replace("-", "")
    if not phone_clean.isdigit() or len(phone_clean) != 10:
        return jsonify({"success": False, "error": "Please enter a valid 10-digit customer phone number."}), 400

    if not cart_items:
        return jsonify({"success": False, "error": "Cart is empty. Please add products before checkout."}), 400

    db = get_db()
    cursor = db.cursor()

    # Step 1: Verify current stock for every item to prevent overselling
    hydrated_cart = []
    for itm in cart_items:
        p_id = itm.get("product_id")
        qty = int(itm.get("quantity", 0))

        if qty <= 0:
            return jsonify({"success": False, "error": "Invalid item quantity."}), 400

        cursor.execute("SELECT * FROM products WHERE id = ?", (p_id,))
        prod = cursor.fetchone()
        if not prod:
            return jsonify({"success": False, "error": f"Product ID {p_id} does not exist."}), 400

        if prod["stock"] < qty:
            return jsonify({
                "success": False,
                "error": f"Insufficient stock for '{prod['name']}'. Requested: {qty}, Available: {prod['stock']}."
            }), 400

        hydrated_cart.append({
            "id": prod["id"],
            "product_code": prod["product_code"],
            "name": prod["name"],
            "category": prod["category"],
            "cost_price": prod["cost_price"],
            "selling_price": prod["selling_price"],
            "stock": prod["stock"],
            "threshold": prod["threshold"],
            "gst_rate": prod["gst_rate"],
            "quantity": qty
        })

    # Step 2: Compute finalized financials
    fin = calculate_bill_financials(hydrated_cart)

    # Step 3: Validate payment amount
    if payment_mode == "Cash":
        if amount_paid < fin["grand_total"]:
            short = round(fin["grand_total"] - amount_paid, 2)
            return jsonify({"success": False, "error": f"Insufficient cash tendered! Short by Rs. {short:.2f}."}), 400
        change_due = round(amount_paid - fin["grand_total"], 2)
    else:
        amount_paid = fin["grand_total"]
        change_due = 0.0

    now = datetime.datetime.now()
    bill_date = now.strftime("%d/%m/%Y")
    bill_time = now.strftime("%H:%M:%S")
    bill_no = generate_unique_bill_no(db)

    try:
        # Step 4: Upsert Customer
        cursor.execute("SELECT id, bill_count, total_purchases FROM customers WHERE phone = ?", (phone_clean,))
        cust = cursor.fetchone()
        if cust:
            cust_id = cust["id"]
            new_count = cust["bill_count"] + 1
            new_total = cust["total_purchases"] + fin["grand_total"]
            cursor.execute("""
                UPDATE customers SET name = ?, email = ?, bill_count = ?, total_purchases = ?
                WHERE id = ?
            """, (customer_name, customer_email, new_count, new_total, cust_id))
        else:
            cursor.execute("""
                INSERT INTO customers (name, phone, email, bill_count, total_purchases)
                VALUES (?, ?, ?, 1, ?)
            """, (customer_name, phone_clean, customer_email, fin["grand_total"]))
            cust_id = cursor.lastrowid

        # Step 5: Insert Bill Record
        cursor.execute("""
            INSERT INTO bills (
                bill_no, customer_id, customer_name, customer_phone,
                bill_date, bill_time, subtotal, discount, taxable_amount,
                total_gst, grand_total, payment_mode, amount_paid, change_due,
                payment_ref, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_no, cust_id, customer_name, phone_clean,
            bill_date, bill_time, fin["gross_subtotal"], fin["total_discount"],
            fin["overall_taxable"], fin["total_gst"], fin["grand_total"],
            payment_mode, amount_paid, change_due, payment_ref, session.get("user_id")
        ))
        bill_id = cursor.lastrowid

        # Step 6: Insert Line Items & Deduct Inventory Stock
        post_sale_alerts = []
        for line in fin["items"]:
            cursor.execute("""
                INSERT INTO bill_items (
                    bill_id, product_id, product_code, product_name, category,
                    cost_price, selling_price, quantity, subtotal, item_discount,
                    taxable_amount, gst_rate, gst_amount, item_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_id, line["product_id"], line["product_code"], line["product_name"],
                line["category"], line["cost_price"], line["selling_price"],
                line["quantity"], line["subtotal"], line["item_discount"],
                line["taxable_amount"], line["gst_rate"], line["gst_amount"], line["item_total"]
            ))

            # Deduct stock
            cursor.execute("""
                UPDATE products SET stock = stock - ? WHERE id = ?
            """, (line["quantity"], line["product_id"]))

            # Check new stock for post-sale alert
            cursor.execute("SELECT name, stock, threshold FROM products WHERE id = ?", (line["product_id"],))
            upd = cursor.fetchone()
            if upd:
                if upd["stock"] == 0:
                    post_sale_alerts.append(f"'{upd['name']}' is now OUT OF STOCK!")
                elif upd["stock"] <= upd["threshold"]:
                    post_sale_alerts.append(f"'{upd['name']}' is LOW ON STOCK ({upd['stock']} left, threshold: {upd['threshold']})")

        db.commit()

        # Build response payload for instant receipt generation
        receipt_data = {
            "bill_id": bill_id,
            "bill_no": bill_no,
            "date": bill_date,
            "time": bill_time,
            "customer_name": customer_name,
            "customer_phone": phone_clean,
            "items": fin["items"],
            "subtotal": fin["gross_subtotal"],
            "discount_breakdown": {
                "qty_discount": fin["total_qty_discount"],
                "bill_discount": fin["bill_disc_amt"],
                "bill_discount_rate": fin["bill_disc_rate"],
                "total_discount": fin["total_discount"]
            },
            "taxable_amount": fin["overall_taxable"],
            "total_gst": fin["total_gst"],
            "grand_total": fin["grand_total"],
            "payment_mode": payment_mode,
            "amount_paid": amount_paid,
            "change_due": change_due,
            "payment_ref": payment_ref,
            "cashier": session.get("full_name", "Cashier"),
            "alerts": post_sale_alerts
        }

        return jsonify({"success": True, "bill": receipt_data})

    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": f"Database transaction failed: {str(e)}"}), 500


# ------------------------------------------------------------------------------
# PRODUCT CATALOGUE MANAGEMENT (CRUD)
# ------------------------------------------------------------------------------
@app.route("/products")
@login_required
def products():
    db = get_db()
    cursor = db.cursor()

    query = request.args.get("q", "").strip()
    category = request.args.get("cat", "").strip()
    sort_by = request.args.get("sort", "name_asc")

    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if query:
        sql += " AND (product_code LIKE ? OR name LIKE ? OR category LIKE ?)"
        term = f"%{query}%"
        params.extend([term, term, term])

    if category:
        sql += " AND category = ?"
        params.append(category)

    # Sort options
    if sort_by == "price_asc":
        sql += " ORDER BY selling_price ASC"
    elif sort_by == "price_desc":
        sql += " ORDER BY selling_price DESC"
    elif sort_by == "stock_asc":
        sql += " ORDER BY stock ASC"
    elif sort_by == "stock_desc":
        sql += " ORDER BY stock DESC"
    else:
        sql += " ORDER BY name ASC"

    cursor.execute(sql, params)
    product_list = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = [r[0] for r in cursor.fetchall()]

    return render_template(
        "products.html",
        products=product_list,
        categories=categories,
        current_query=query,
        current_cat=category,
        current_sort=sort_by
    )


@app.route("/products/add", methods=["POST"])
@login_required
@admin_required
def product_add():
    code = request.form.get("product_code", "").strip().upper()
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    cost_price = float(request.form.get("cost_price", 0.0))
    selling_price = float(request.form.get("selling_price", 0.0))
    stock = int(request.form.get("stock", 0))
    threshold = int(request.form.get("threshold", 5))
    gst_rate = float(request.form.get("gst_rate", 18.0))

    if not code or not name or not category:
        flash("Product Code, Name, and Category are mandatory.", "danger")
        return redirect(url_for("products"))

    if selling_price < 0 or cost_price < 0 or stock < 0 or threshold < 0:
        flash("Prices and stock numbers cannot be negative.", "danger")
        return redirect(url_for("products"))

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (product_code, name, category, cost_price, selling_price, stock, threshold, gst_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, name, category, cost_price, selling_price, stock, threshold, gst_rate))
        db.commit()
        flash(f"Product '{name}' [{code}] added successfully!", "success")
    except sqlite3.IntegrityError:
        flash(f"Error: Product Code '{code}' already exists in catalogue.", "danger")

    return redirect(url_for("products"))


@app.route("/products/edit/<int:id>", methods=["POST"])
@login_required
@admin_required
def product_edit(id):
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    cost_price = float(request.form.get("cost_price", 0.0))
    selling_price = float(request.form.get("selling_price", 0.0))
    stock = int(request.form.get("stock", 0))
    threshold = int(request.form.get("threshold", 5))
    gst_rate = float(request.form.get("gst_rate", 18.0))

    if not name or not category:
        flash("Product name and category cannot be empty.", "danger")
        return redirect(url_for("products"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, cost_price = ?, selling_price = ?,
            stock = ?, threshold = ?, gst_rate = ?
        WHERE id = ?
    """, (name, category, cost_price, selling_price, stock, threshold, gst_rate, id))
    db.commit()
    flash(f"Product '{name}' updated successfully!", "success")
    return redirect(url_for("products"))


@app.route("/products/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def product_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM products WHERE id = ?", (id,))
    prod = cursor.fetchone()
    if prod:
        cursor.execute("DELETE FROM products WHERE id = ?", (id,))
        db.commit()
        flash(f"Product '{prod['name']}' removed from catalogue.", "success")
    return redirect(url_for("products"))


# ------------------------------------------------------------------------------
# INVENTORY MANAGEMENT
# ------------------------------------------------------------------------------
@app.route("/inventory")
@login_required
def inventory():
    db = get_db()
    cursor = db.cursor()

    filter_type = request.args.get("filter", "all")

    if filter_type == "low":
        cursor.execute("SELECT * FROM products WHERE stock > 0 AND stock <= threshold ORDER BY stock ASC")
    elif filter_type == "out":
        cursor.execute("SELECT * FROM products WHERE stock = 0 ORDER BY name ASC")
    else:
        cursor.execute("SELECT * FROM products ORDER BY stock ASC")

    product_list = cursor.fetchall()

    # Counts
    cursor.execute("SELECT COUNT(*) FROM products")
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock > threshold")
    healthy_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock > 0 AND stock <= threshold")
    low_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock = 0")
    out_count = cursor.fetchone()[0]

    counts = {
        "total": total_count,
        "healthy": healthy_count,
        "low": low_count,
        "out": out_count
    }

    return render_template("inventory.html", products=product_list, counts=counts, current_filter=filter_type)


@app.route("/inventory/restock", methods=["POST"])
@login_required
def inventory_restock():
    product_id = int(request.form.get("product_id"))
    units = int(request.form.get("quantity", 0))

    if units <= 0:
        flash("Restock quantity must be at least 1 unit.", "danger")
        return redirect(url_for("inventory"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (units, product_id))
    db.commit()

    cursor.execute("SELECT name, stock FROM products WHERE id = ?", (product_id,))
    prod = cursor.fetchone()
    flash(f"Successfully restocked {units} units for '{prod['name']}'. New stock: {prod['stock']}.", "success")
    return redirect(url_for("inventory"))


# ------------------------------------------------------------------------------
# CUSTOMER MANAGEMENT
# ------------------------------------------------------------------------------
@app.route("/customers")
@login_required
def customers():
    db = get_db()
    cursor = db.cursor()

    query = request.args.get("q", "").strip()
    if query:
        term = f"%{query}%"
        cursor.execute("""
            SELECT * FROM customers
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY name ASC
        """, (term, term, term))
    else:
        cursor.execute("SELECT * FROM customers ORDER BY total_purchases DESC")

    customer_list = cursor.fetchall()
    return render_template("customers.html", customers=customer_list, current_query=query)


@app.route("/customers/add", methods=["POST"])
@login_required
def customer_add():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip().replace(" ", "").replace("-", "")
    email = request.form.get("email", "").strip()

    if not name or not phone:
        flash("Customer Name and Phone are required.", "danger")
        return redirect(url_for("customers"))

    if not phone.isdigit() or len(phone) != 10:
        flash("Please enter a valid 10-digit mobile number.", "danger")
        return redirect(url_for("customers"))

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO customers (name, phone, email)
            VALUES (?, ?, ?)
        """, (name, phone, email))
        db.commit()
        flash(f"Customer '{name}' registered successfully!", "success")
    except sqlite3.IntegrityError:
        flash(f"Customer with phone number {phone} is already registered.", "warning")

    return redirect(url_for("customers"))


@app.route("/customers/edit/<int:id>", methods=["POST"])
@login_required
def customer_edit(id):
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip().replace(" ", "").replace("-", "")
    email = request.form.get("email", "").strip()

    if not name or not phone:
        flash("Customer name and phone cannot be empty.", "danger")
        return redirect(url_for("customers"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE customers SET name = ?, phone = ?, email = ? WHERE id = ?
    """, (name, phone, email, id))
    db.commit()
    flash(f"Customer profile for '{name}' updated.", "success")
    return redirect(url_for("customers"))


@app.route("/customers/<int:id>/bills")
@login_required
def customer_bills(id):
    """View purchase history for a specific customer."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (id,))
    customer = cursor.fetchone()
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for("customers"))

    cursor.execute("SELECT * FROM bills WHERE customer_id = ? ORDER BY id DESC", (id,))
    bills_list = cursor.fetchall()
    return render_template("customer_bills.html", customer=customer, bills=bills_list)


# ------------------------------------------------------------------------------
# BILL HISTORY & INVOICE REPRINTING
# ------------------------------------------------------------------------------
@app.route("/bills")
@login_required
def bills():
    db = get_db()
    cursor = db.cursor()

    query = request.args.get("q", "").strip()
    date_filter = request.args.get("date", "").strip()

    sql = "SELECT b.*, u.full_name as cashier_name FROM bills b LEFT JOIN users u ON b.user_id = u.id WHERE 1=1"
    params = []

    if query:
        sql += " AND (b.bill_no LIKE ? OR b.customer_name LIKE ? OR b.customer_phone LIKE ?)"
        term = f"%{query}%"
        params.extend([term, term, term])

    if date_filter:
        # Convert HTML YYYY-MM-DD to DD/MM/YYYY
        try:
            d_obj = datetime.datetime.strptime(date_filter, "%Y-%m-%d")
            formatted_date = d_obj.strftime("%d/%m/%Y")
            sql += " AND b.bill_date = ?"
            params.append(formatted_date)
        except ValueError:
            pass

    sql += " ORDER BY b.id DESC LIMIT 100"
    cursor.execute(sql, params)
    bill_list = cursor.fetchall()

    return render_template("bills.html", bills=bill_list, current_query=query, current_date=date_filter)


@app.route("/bills/<int:id>")
@login_required
def bill_detail(id):
    """Fetch complete bill and line items for viewing and reprinting receipt."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT b.*, u.full_name as cashier_name
        FROM bills b
        LEFT JOIN users u ON b.user_id = u.id
        WHERE b.id = ?
    """, (id,))
    bill = cursor.fetchone()
    if not bill:
        return jsonify({"error": "Invoice not found"}), 404

    cursor.execute("SELECT * FROM bill_items WHERE bill_id = ?", (id,))
    items = cursor.fetchall()

    items_data = []
    for itm in items:
        items_data.append({
            "product_code": itm["product_code"],
            "product_name": itm["product_name"],
            "category": itm["category"],
            "selling_price": itm["selling_price"],
            "quantity": itm["quantity"],
            "subtotal": itm["subtotal"],
            "item_discount": itm["item_discount"],
            "taxable_amount": itm["taxable_amount"],
            "gst_rate": itm["gst_rate"],
            "gst_amount": itm["gst_amount"],
            "item_total": itm["item_total"]
        })

    bill_dict = {
        "id": bill["id"],
        "bill_no": bill["bill_no"],
        "customer_name": bill["customer_name"],
        "customer_phone": bill["customer_phone"],
        "date": bill["bill_date"],
        "time": bill["bill_time"],
        "subtotal": bill["subtotal"],
        "discount": bill["discount"],
        "taxable_amount": bill["taxable_amount"],
        "total_gst": bill["total_gst"],
        "grand_total": bill["grand_total"],
        "payment_mode": bill["payment_mode"],
        "amount_paid": bill["amount_paid"],
        "change_due": bill["change_due"],
        "payment_ref": bill["payment_ref"],
        "cashier": bill["cashier_name"] or "Cashier",
        "items": items_data
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("format") == "json":
        return jsonify(bill_dict)

    return render_template("bill_detail.html", bill=bill_dict)


# ------------------------------------------------------------------------------
# SALES REPORTS & ANALYTICS
# ------------------------------------------------------------------------------
@app.route("/reports")
@login_required
def reports():
    db = get_db()
    cursor = db.cursor()

    time_range = request.args.get("range", "all")
    today_str = datetime.date.today().strftime("%d/%m/%Y")

    sql_bills = "SELECT * FROM bills"
    sql_items = "SELECT * FROM bill_items"

    if time_range == "today":
        sql_bills += f" WHERE bill_date = '{today_str}'"
        cursor.execute(f"SELECT id FROM bills WHERE bill_date = '{today_str}'")
        b_ids = [str(r[0]) for r in cursor.fetchall()]
        if b_ids:
            sql_items += f" WHERE bill_id IN ({','.join(b_ids)})"
        else:
            sql_items += " WHERE 1=0"

    cursor.execute(sql_bills)
    bills_list = cursor.fetchall()

    cursor.execute(sql_items)
    items_list = cursor.fetchall()

    total_revenue = sum(b["grand_total"] for b in bills_list)
    total_bills = len(bills_list)
    total_gst = sum(b["total_gst"] for b in bills_list)
    total_discounts = sum(b["discount"] for b in bills_list)
    total_units_sold = sum(i["quantity"] for i in items_list)
    avg_basket = (total_revenue / total_bills) if total_bills > 0 else 0.0

    # Profit estimation: sum of (selling_price - cost_price) * quantity for each sold item
    total_cost = sum(i["cost_price"] * i["quantity"] for i in items_list)
    total_profit = max(0.0, sum((i["taxable_amount"] - (i["cost_price"] * i["quantity"])) for i in items_list))

    # Top selling products
    cursor.execute("""
        SELECT product_name, category, SUM(quantity) as qty, SUM(item_total) as revenue,
               SUM(taxable_amount - (cost_price * quantity)) as estimated_profit
        FROM bill_items
        GROUP BY product_id
        ORDER BY qty DESC LIMIT 8
    """)
    product_performance = cursor.fetchall()

    # Payment mode counts
    payment_stats = {"Cash": 0, "UPI": 0, "Card": 0}
    for b in bills_list:
        m = b["payment_mode"]
        payment_stats[m] = payment_stats.get(m, 0) + 1

    summary = {
        "total_revenue": total_revenue,
        "total_bills": total_bills,
        "total_gst": total_gst,
        "total_discounts": total_discounts,
        "total_units_sold": total_units_sold,
        "avg_basket": avg_basket,
        "total_profit": total_profit,
        "payment_stats": payment_stats
    }

    return render_template(
        "reports.html",
        summary=summary,
        product_performance=product_performance,
        current_range=time_range
    )


@app.route("/api/chart-data")
@login_required
def api_chart_data():
    """Provides structured JSON data for interactive Chart.js visualizations."""
    db = get_db()
    cursor = db.cursor()

    # 1. Sales Trend over the last 7 distinct dates
    cursor.execute("""
        SELECT bill_date, SUM(grand_total) as daily_rev, COUNT(*) as bill_count
        FROM bills
        GROUP BY bill_date
        ORDER BY id DESC LIMIT 7
    """)
    trend_rows = cursor.fetchall()
    trend_rows = list(reversed(trend_rows))

    trend_labels = [r["bill_date"] for r in trend_rows]
    trend_revenue = [round(r["daily_rev"], 2) for r in trend_rows]

    # 2. Top 5 Products by Quantity
    cursor.execute("""
        SELECT product_name, SUM(quantity) as total_qty
        FROM bill_items
        GROUP BY product_id
        ORDER BY total_qty DESC LIMIT 5
    """)
    top_rows = cursor.fetchall()
    top_labels = [r["product_name"] for r in top_rows]
    top_quantities = [r["total_qty"] for r in top_rows]

    # 3. Payment Mode Split
    cursor.execute("""
        SELECT payment_mode, COUNT(*) as cnt, SUM(grand_total) as total
        FROM bills
        GROUP BY payment_mode
    """)
    pay_rows = cursor.fetchall()
    pay_labels = [r["payment_mode"] for r in pay_rows]
    pay_counts = [r["cnt"] for r in pay_rows]

    return jsonify({
        "sales_trend": {
            "labels": trend_labels,
            "data": trend_revenue
        },
        "top_products": {
            "labels": top_labels,
            "data": top_quantities
        },
        "payment_distribution": {
            "labels": pay_labels,
            "data": pay_counts
        }
    })


# ------------------------------------------------------------------------------
# SERVER ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  SMARTBILL – Retail Billing & Inventory Management System")
    print("  Server is starting on: http://127.0.0.1:5000")
    print("  Default Admin Login  : admin / admin123")
    print("  Default Cashier Login: cashier / cashier123")
    print("=" * 65 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
