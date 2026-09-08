# SmartBill – Smart Billing & Inventory Management System

**SmartBill** is a modern, full-stack Point-of-Sale (POS) and inventory management web application developed in Python (Flask) and SQLite. Designed to fulfill the B.Tech Computer Science & Engineering (CSE) curriculum requirements, it transforms a standard bill generator assignment into a commercial-grade retail store management system.

---

## 1. Project Abstract

Traditional billing software assignments typically implement basic terminal calculators that require cashiers to manually type prices without inventory tracking, multi-tax calculations, or persistent records. **SmartBill** addresses these limitations by providing an intuitive, browser-based web application with real-time stock synchronization, automatic tiered discounting, multi-slab Goods & Services Tax (GST) calculation, dynamic customer management, and visual sales analytics. Built using Python, Flask, SQLite, HTML5, CSS3, JavaScript, and Chart.js, the system operates completely offline without external cloud dependencies, making it reliable, cross-platform, and ideal for B.Tech project demonstrations and technical vivas.

---

## 2. Key Objectives

1. **Automate Store Operations**: Eliminate manual price entry and handwritten slips through a fast, search-driven POS billing terminal.
2. **Real-Time Inventory Synchronization**: Automatically deduct purchased stock upon payment confirmation and block overselling or negative stock.
3. **Smart Tiered Pricing**: Encourage bulk purchasing using transparent, rule-based quantity and basket-level discounts.
4. **Statutory GST Compliance**: Apply distinct tax slabs (5%, 12%, 18%) per product category on the net taxable amount.
5. **Multi-Mode Payment Handling**: Support Cash (with automatic change due calculation), UPI, and Card transactions.
6. **Customer Retention**: Track customer purchase history, total lifetime spending, and invoice frequency.
7. **Business Intelligence**: Provide store owners with interactive visual dashboards, revenue trends, top-selling items, and estimated profit analysis.

---

## 3. Technology Stack

* **Backend**: Python 3.8+, Flask 3.x
* **Database**: SQLite3 (relational, persistent, zero-configuration)
* **Frontend**: HTML5, CSS3 (Custom Responsive Design System), Vanilla JavaScript (ES6)
* **Visualizations**: Chart.js (CDN for interactive charts)
* **Security & Auth**: Werkzeug password hashing (`generate_password_hash` / `check_password_hash`) and session-based role access control.

---

## 4. User Roles & Default Credentials

| Role | Username | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full access: Add/Edit/Delete products, manage inventory, view profit analytics, register customers, billing |
| **Cashier** | `cashier` | `cashier123` | Operational access: POS billing, customer directory, view product catalogue, view invoices |

---

## 5. Project Structure

```
SmartBill/
│
├── app.py                   # Flask server, route controllers, calculations & SQLite models
├── database.db              # SQLite relational database (auto-seeded on launch)
├── requirements.txt         # Python dependencies (Flask, Werkzeug)
│
├── templates/
│   ├── base.html            # Main layout with responsive sidebar, navbar & toast alerts
│   ├── login.html           # Secure sign-in page with 1-click viva credentials fill
│   ├── dashboard.html       # Analytics overview, KPI cards, sales graph & low-stock alerts
│   ├── billing.html         # Modern POS cashier terminal with live cart & search
│   ├── products.html        # Product catalogue with CRUD modals & profit margins
│   ├── inventory.html       # Stock tracking, health status pills & quick restock modal
│   ├── customers.html       # Customer directory with lifetime spend & invoice counts
│   ├── customer_bills.html  # Customer-specific purchase history & past bills
│   ├── bills.html           # Historical invoices table with date & phone search
│   ├── bill_detail.html     # Full receipt view with one-click print styling
│   └── reports.html         # Sales analytics, profit insights & 3 Chart.js graphs
│
├── static/
│   ├── css/
│   │   └── style.css        # Clean CSS design system with @media print support
│   └── js/
│       ├── main.js          # Sidebar toggle, modal controllers & toasts
│       └── billing.js       # Live product search, cart math, change due & checkout
│
├── test_web_app.py          # Automated integration test suite
└── README.md                # Comprehensive documentation & viva preparation guide
```

---

## 6. How to Run the Application

### Step 1: Install Dependencies
Open your terminal and install Flask (if not already installed):
```bash
pip install -r requirements.txt
```

### Step 2: Launch the Web Application
```bash
python app.py
```

### Step 3: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Step 4: Run Automated Tests
```bash
python test_web_app.py
```

---

## 7. Database Schema (SQLite)

The SQLite database (`database.db`) uses normalized relational tables:

1. **`users`**: `id`, `username`, `password_hash`, `full_name`, `role`, `created_at`
2. **`products`**: `id`, `product_code`, `name`, `category`, `cost_price`, `selling_price`, `stock`, `threshold`, `gst_rate`, `created_at`
3. **`customers`**: `id`, `name`, `phone`, `email`, `total_purchases`, `bill_count`, `created_at`
4. **`bills`**: `id`, `bill_no`, `customer_id`, `customer_name`, `customer_phone`, `bill_date`, `bill_time`, `subtotal`, `discount`, `taxable_amount`, `total_gst`, `grand_total`, `payment_mode`, `amount_paid`, `change_due`, `payment_ref`, `user_id`, `created_at`
5. **`bill_items`**: `id`, `bill_id`, `product_id`, `product_code`, `product_name`, `category`, `cost_price`, `selling_price`, `quantity`, `subtotal`, `item_discount`, `taxable_amount`, `gst_rate`, `gst_amount`, `item_total`

---

## 8. Screen-by-Screen Walkthrough

### 1. Dashboard (`/dashboard`)
* **KPI Metric Cards**: Real-time sales today, total bills count, active products count, low-stock warning count, total registered customers, and GST collected.
* **Revenue Trend Chart**: Visual Chart.js line graph showing daily sales trajectory.
* **Low Stock Alert Box**: Highlights products that require reordering (`stock <= threshold`).
* **Recent Invoices**: Latest 5 customer transactions with instant receipt links.

### 2. POS Billing Terminal (`/billing`)
* **Customer Lookup**: Input customer name and 10-digit mobile number.
* **Fast Product Search**: Type name, category, or code (`P101`) to view live shelf stock, price, and GST slab.
* **Interactive Cart Table**: Increase/decrease quantities with `+`/`-` buttons, calculate subtotal, and remove items.
* **Real-time Pricing Breakdown**:
  * Gross Subtotal
  * Bulk Quantity Discount (5% for 5-9 units, 10% for 10+ units)
  * Store Basket Offer (5% for $\ge$ Rs. 1,000; 10% for $\ge$ Rs. 5,000; 15% for $\ge$ Rs. 10,000)
  * Net Taxable Value
  * Multi-slab GST (5%, 12%, 18%)
  * Grand Total
* **Payment Modes**:
  * **Cash**: Enters cash received; computes live `Change Due = Amount Paid - Grand Total`.
  * **UPI**: Captures transaction reference / UTR ID.
  * **Card**: Records last 4 digits / authorization ID.
* **Printable Receipt**: Generates a professional store receipt modal with one-click `window.print()` formatting.

### 3. Product Catalogue (`/products`)
* Full CRUD: Add product, Edit product, Delete product.
* Search by keyword and filter by category.
* Sort by price (low/high) and stock (low/high).
* Margin insight: Displays gross profit percentage based on `(Selling Price - Cost Price) / Selling Price`.

### 4. Inventory Control (`/inventory`)
* Visual status pills: `IN STOCK` (green), `LOW STOCK` (amber), `OUT OF STOCK` (red).
* Quick Restock modal: Instantly increment on-hand inventory units without altering product specifications.

### 5. Customer Directory (`/customers`)
* Search customers by name or phone.
* View total purchases and purchase count.
* Access dedicated customer invoice history.

### 6. Bill History (`/bills`)
* Comprehensive transaction archive.
* Filter by date picker and search by invoice ID or phone.
* Reprint formatted invoices.

### 7. Sales Reports & Profit Analytics (`/reports`)
* Time filter: *All Time* or *Today's Sales*.
* High-level metrics: Net Sales Revenue, Estimated Gross Profit, Invoices Count, GST, Discounts, Average Basket Value.
* 3 Interactive Chart.js Graphs:
  1. Revenue Trend Line Chart
  2. Payment Modes Split Doughnut Chart
  3. Top Selling Products Bar Chart
* Product-level profit analysis table.

---

## 9. 25 Likely Viva Questions & Simple Answers

### Q1: What is the main purpose of SmartBill?
**Answer**: SmartBill is a retail Point-of-Sale (POS) and inventory web application that automates customer bill generation, applies smart discounts, calculates category-specific GST, tracks inventory in real-time, and provides store analytics.

### Q2: Why did you choose Flask over Django or other frameworks?
**Answer**: Flask is a lightweight microframework that provides routing, request handling, and Jinja2 templating without the heavy boilerplate of Django. This makes the architecture transparent and easy to explain during a viva.

### Q3: Why did you use SQLite for database management?
**Answer**: SQLite is serverless, zero-configuration, and integrated into Python's standard library (`sqlite3`). It stores data in a single file (`database.db`), ensuring full ACID compliance and data persistence across application restarts.

### Q4: How is GST calculated in the application?
**Answer**: GST is calculated on the *net taxable value* of each product after applying discounts. If a bill-level discount is applied, it is distributed proportionally across line items. Then each item's tax is computed as:
$$\text{GST Amount} = \text{Taxable Amount} \times \frac{\text{GST Rate}}{100}$$
The total GST is the sum of taxes across all line items.

### Q5: What is the discount structure implemented in SmartBill?
**Answer**: SmartBill uses a dual-tier discount system:
1. **Quantity Discount**: 5% on a line item for 5–9 units; 10% for 10+ units.
2. **Bill-Value Discount**: 5% off for bills $\ge$ Rs. 1,000; 10% off for bills $\ge$ Rs. 5,000; 15% off for bills $\ge$ Rs. 10,000.

### Q6: How does the system prevent overselling or negative stock?
**Answer**: During checkout, the server verifies current stock in SQLite:
`if product.stock < requested_quantity: abort with 400 Insufficient Stock`.
Stock is only decremented inside an atomic SQLite transaction upon successful checkout.

### Q7: When is stock deducted from inventory?
**Answer**: Stock is deducted only after payment validation. If the cashier removes items or cancels the bill during cart editing, no stock is deducted.

### Q8: How does the Cash change calculation work?
**Answer**: When the cashier enters the cash tendered by the customer, the frontend validates that `amount_paid >= grand_total` and computes:
$$\text{Change Due} = \text{Amount Paid} - \text{Grand Total}$$
The backend re-validates this before storing the invoice.

### Q9: How are unique bill numbers generated?
**Answer**: The system generates invoice IDs using `BILL-YYYYMMDD-XXXX`, where `YYYYMMDD` is the current date and `XXXX` is a 4-digit zero-padded sequential counter based on the number of invoices generated on that day.

### Q10: How does role-based access control (RBAC) work?
**Answer**: The system uses session authentication. When a user logs in, their `role` (Admin or Cashier) is stored in the Flask session. Routes modifying products (`/products/add`, `/products/delete`) use an `@admin_required` decorator that redirects unauthorized Cashiers with an access-denied flash message.

### Q11: How are passwords stored securely?
**Answer**: Passwords are never stored in plaintext. They are hashed using Werkzeug's `generate_password_hash` (PBKDF2/SHA-256) and verified using `check_password_hash`.

### Q12: What is the purpose of the low-stock threshold?
**Answer**: Each product has a configurable `threshold` (default: 5 units). If stock drops below this number, it triggers visual warning badges on the dashboard and inventory page so store managers can reorder before stock runs out.

### Q13: What is Jinja2 and how is it used?
**Answer**: Jinja2 is Flask's templating engine. It enables server-side rendering of dynamic HTML pages using control tags (`{% for %}`, `{% if %}`) and expression tags (`{{ variable }}`). It also supports template inheritance via `{% extends "base.html" %}`.

### Q14: How does the live product search work in the POS interface?
**Answer**: The search bar uses an `input` event listener with a 200ms debounce timer. It sends an asynchronous `fetch()` request to `/api/products/search?q=term`, which queries SQLite and returns matching products in JSON to populate the dropdown.

### Q15: How does the printable invoice work?
**Answer**: The invoice modal contains a `.receipt-paper` container styled with standard receipt typography. CSS `@media print` rules hide the sidebar, header, and buttons, allowing clean printing or saving to PDF via the browser's native print dialogue (`window.print()`).

### Q16: How is estimated gross profit calculated?
**Answer**: Every product stores both `cost_price` and `selling_price`. For each sold item, profit is calculated as:
$$\text{Profit} = \text{Taxable Line Revenue} - (\text{Cost Price} \times \text{Quantity})$$
The sum across all sold items represents the store's estimated gross profit.

### Q17: What are HTTP methods used in this project?
**Answer**: `GET` is used to retrieve web pages and query product/bill data without modifying state. `POST` is used for state-changing operations such as login, checkout, adding products, editing, and restocking.

### Q18: What is the purpose of `app.teardown_appcontext`?
**Answer**: It ensures that open SQLite database connections stored in Flask's `g` object are properly closed at the end of each HTTP request to prevent database locks and memory leaks.

### Q19: What is a primary key and foreign key in this project?
**Answer**: 
- **Primary Key**: `id` in tables like `products` or `bills` uniquely identifies each record.
- **Foreign Key**: `customer_id` in `bills` references `customers.id`, and `bill_id` in `bill_items` references `bills.id`.

### Q20: How are input validation errors handled?
**Answer**: Inputs are validated both on the client side (HTML5 `required`, input types) and on the server side (checking for empty fields, regex validation for 10-digit phone numbers, and non-negative numeric constraints). User-friendly flash messages or JSON errors are returned.

### Q21: What is Chart.js and how does it receive data?
**Answer**: Chart.js is an open-source JavaScript visualization library. The frontend fetches data from the `/api/chart-data` Flask route, which performs SQL aggregations (`GROUP BY bill_date`, `GROUP BY payment_mode`), and renders canvas graphs.

### Q22: What happens if `database.db` is deleted?
**Answer**: The application includes `init_db()` and `seed_database()` functions that automatically re-create all tables and insert 12 sample products and default user accounts upon restarting `app.py`.

### Q23: What are the advantages of this system over a basic bill generator?
**Answer**: It features a persistent relational database, live inventory tracking with low-stock alerts, multi-slab GST calculation, dual-tier discounts, customer purchase history, payment method tracking, and an analytics dashboard with profit estimation.

### Q24: What are the limitations of this application?
**Answer**: It runs locally on a single machine, uses simulated UPI/Card entries instead of live bank payment gateways, and lacks physical barcode scanner integration.

### Q25: What future enhancements could be added?
**Answer**: 
1. Real-time barcode / QR code hardware scanner support.
2. Integration with payment gateways (Razorpay / Stripe) and SMS/WhatsApp digital receipts (Twilio).
3. Migration to PostgreSQL for multi-store network synchronization.

---

## 10. College Presentation & Report Content

### Existing System vs Proposed System

| Feature | Existing System (Manual / Basic Script) | Proposed System (SmartBill) |
|---|---|---|
| **Interface** | Terminal CLI / Handwritten paper slips | Modern responsive browser dashboard & POS |
| **Price Entry** | Cashier types price manually (error-prone) | Automated lookup from database |
| **Stock Control** | None (items can be sold infinitely) | Real-time stock decrement & low-stock alerts |
| **Taxes & GST** | Single flat tax or manual calculation | Itemized multi-slab GST (5%, 12%, 18%) post-discount |
| **Discounts** | Ad-hoc / manual entry | Automated quantity & basket value discount tiers |
| **Customer Tracking** | Paper register / none | Persistent customer profiles and spend history |
| **Analytics** | Manual end-of-day tally | Real-time visual revenue, top products, and profit graphs |

---

## 11. License & Academic Attribution
Developed as an educational mini project for B.Tech Computer Science & Engineering. Open for academic learning, viva presentations, and project submissions.
