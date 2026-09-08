"""
================================================================================
SmartBill – Smart Store Billing and Inventory Management System
================================================================================
A complete, robust, terminal-based retail billing and inventory management
application developed in Python. Designed for retail stores and ideal for a
B.Tech CSE Python mini project & viva demonstration.

Features:
- Product Catalogue management (CRUD operations)
- Real-time stock tracking with low-stock & out-of-stock warnings
- Interactive shopping cart with live validation
- Dual-tier smart discounts (item quantity discount + bill value tiered discount)
- Accurate item-wise GST calculation across multiple tax slabs (5%, 12%, 18%)
- Multiple payment modes (Cash with change calculation, UPI, Card)
- Automatic inventory deduction upon successful billing
- Persistent data storage using JSON (products.json & bills.json)
- Bill history viewing and formatted receipt reprinting
- Comprehensive daily sales summary & business analytics
- Flexible product search (by ID, Name, or Category)
- Robust error handling and defensive input validation
- Universal console compatibility (safe encoding for Windows & Linux)
================================================================================
"""

import os
import sys
import json
import datetime

# ------------------------------------------------------------------------------
# UNIVERSAL CONSOLE ENCODING COMPATIBILITY
# ------------------------------------------------------------------------------
# Ensure safe output stream encoding on Windows terminals (cmd.exe, PowerShell)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Universal currency symbol (Rs. is 100% compatible across all Windows codepages)
CURRENCY = "Rs."

# ------------------------------------------------------------------------------
# FILE PATHS & PERSISTENCE CONFIGURATION
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")
BILLS_FILE = os.path.join(BASE_DIR, "bills.json")

# Default 10 realistic sample products representing various store categories & GST slabs
DEFAULT_PRODUCTS = [
    {
        "id": "P101",
        "name": "Wireless Optical Mouse",
        "category": "Electronics",
        "price": 499.00,
        "stock": 25,
        "threshold": 5,
        "gst_rate": 18.0
    },
    {
        "id": "P102",
        "name": "Mechanical Gaming Keyboard",
        "category": "Electronics",
        "price": 1899.00,
        "stock": 15,
        "threshold": 3,
        "gst_rate": 18.0
    },
    {
        "id": "P103",
        "name": "USB-C Fast Cable (1.5m)",
        "category": "Electronics",
        "price": 249.00,
        "stock": 40,
        "threshold": 8,
        "gst_rate": 18.0
    },
    {
        "id": "P104",
        "name": "A4 Spiral Notebook (200p)",
        "category": "Stationery",
        "price": 85.00,
        "stock": 50,
        "threshold": 10,
        "gst_rate": 12.0
    },
    {
        "id": "P105",
        "name": "Gel Pen Set (Pack of 5)",
        "category": "Stationery",
        "price": 120.00,
        "stock": 30,
        "threshold": 6,
        "gst_rate": 12.0
    },
    {
        "id": "P106",
        "name": "Royal Basmati Rice (5 kg)",
        "category": "Groceries",
        "price": 450.00,
        "stock": 20,
        "threshold": 5,
        "gst_rate": 5.0
    },
    {
        "id": "P107",
        "name": "Cold-Pressed Oil (1 L)",
        "category": "Groceries",
        "price": 210.00,
        "stock": 25,
        "threshold": 5,
        "gst_rate": 5.0
    },
    {
        "id": "P108",
        "name": "Dark Roast Coffee (200g)",
        "category": "Beverages",
        "price": 290.00,
        "stock": 20,
        "threshold": 4,
        "gst_rate": 5.0
    },
    {
        "id": "P109",
        "name": "Dark Chocolate Bar (100g)",
        "category": "Confectionery",
        "price": 95.00,
        "stock": 45,
        "threshold": 10,
        "gst_rate": 18.0
    },
    {
        "id": "P110",
        "name": "Herbal Hand Sanitizer (500ml)",
        "category": "Personal Care",
        "price": 110.00,
        "stock": 4,  # Intentionally low stock to demonstrate alert
        "threshold": 5,
        "gst_rate": 18.0
    }
]


def initialize_data_files():
    """Ensure data files exist. If missing or corrupted, initialize with defaults."""
    if not os.path.exists(PRODUCTS_FILE):
        save_products(DEFAULT_PRODUCTS)
    else:
        try:
            with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                json.load(f)
        except (json.JSONDecodeError, IOError):
            print("[System Warning] products.json was corrupted. Re-initializing with sample products.")
            save_products(DEFAULT_PRODUCTS)

    if not os.path.exists(BILLS_FILE):
        save_bills([])
    else:
        try:
            with open(BILLS_FILE, "r", encoding="utf-8") as f:
                json.load(f)
        except (json.JSONDecodeError, IOError):
            print("[System Warning] bills.json was corrupted. Resetting to empty list.")
            save_bills([])


def load_products():
    """Load product catalog from JSON file."""
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to read products: {e}")
        return []


def save_products(products):
    """Save product catalog to JSON file."""
    try:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4)
        return True
    except Exception as e:
        print(f"[Error] Failed to write products: {e}")
        return False


def load_bills():
    """Load bills history from JSON file."""
    try:
        with open(BILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to read bills: {e}")
        return []


def save_bills(bills):
    """Save bills history to JSON file."""
    try:
        with open(BILLS_FILE, "w", encoding="utf-8") as f:
            json.dump(bills, f, indent=4)
        return True
    except Exception as e:
        print(f"[Error] Failed to write bills: {e}")
        return False


# ------------------------------------------------------------------------------
# INPUT VALIDATION HELPERS
# ------------------------------------------------------------------------------
def input_string(prompt, allow_empty=False):
    """Prompt user for a clean, non-empty string."""
    while True:
        val = input(prompt).strip()
        if not val and not allow_empty:
            print("  [!] Input cannot be empty. Please try again.")
            continue
        return val


def input_int(prompt, min_val=None, max_val=None):
    """Prompt user for an integer within optional range [min_val, max_val]."""
    while True:
        val_str = input(prompt).strip()
        try:
            val = int(val_str)
            if min_val is not None and val < min_val:
                print(f"  [!] Value must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  [!] Value must be at most {max_val}.")
                continue
            return val
        except ValueError:
            print("  [!] Invalid input. Please enter an integer number.")


def input_float(prompt, min_val=None, max_val=None):
    """Prompt user for a float within optional range [min_val, max_val]."""
    while True:
        val_str = input(prompt).strip()
        try:
            val = float(val_str)
            if min_val is not None and val < min_val:
                print(f"  [!] Value must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  [!] Value must be at most {max_val}.")
                continue
            return round(val, 2)
        except ValueError:
            print("  [!] Invalid input. Please enter a valid decimal number.")


def input_phone(prompt):
    """Prompt for a standard 10-digit mobile number."""
    while True:
        phone = input(prompt).strip()
        cleaned = phone.replace(" ", "").replace("-", "")
        if cleaned.isdigit() and len(cleaned) == 10:
            return cleaned
        print("  [!] Please enter a valid 10-digit phone number (e.g. 9876543210).")


# ------------------------------------------------------------------------------
# PRODUCT CATALOGUE MANAGEMENT (CRUD)
# ------------------------------------------------------------------------------
def find_product_by_id(products, product_id):
    """Return product dict matching ID (case-insensitive), or None."""
    target = product_id.strip().upper()
    for p in products:
        if p["id"].upper() == target:
            return p
    return None


def display_products_table(product_list, title="PRODUCT CATALOGUE"):
    """Display products in a formatted tabular view with stock status."""
    if not product_list:
        print("\n  [i] No products found.")
        return

    print("\n" + "=" * 86)
    print(f"{title.center(86)}")
    print("=" * 86)
    print(f"{'ID':<6} {'Product Name':<28} {'Category':<14} {f'Price({CURRENCY})':>10} {'Stock':>7} {'GST%':>6} {'Status':<12}")
    print("-" * 86)

    for p in product_list:
        stock = p["stock"]
        threshold = p.get("threshold", 5)
        if stock == 0:
            status = "OUT OF STOCK"
        elif stock <= threshold:
            status = f"LOW ({stock})"
        else:
            status = "OK"

        print(
            f"{p['id']:<6} "
            f"{p['name'][:27]:<28} "
            f"{p['category'][:13]:<14} "
            f"{p['price']:>10.2f} "
            f"{stock:>7} "
            f"{p['gst_rate']:>5.1f}% "
            f"{status:<12}"
        )
    print("=" * 86)


def menu_product_catalogue():
    """Sub-menu for managing the product catalogue."""
    while True:
        products = load_products()
        print("\n" + "-" * 50)
        print("         PRODUCT CATALOGUE MANAGEMENT")
        print("-" * 50)
        print("  [1] View All Products")
        print("  [2] Add New Product")
        print("  [3] Update Product Price")
        print("  [4] Update Product Stock")
        print("  [5] Remove a Product")
        print("  [6] Search Products")
        print("  [0] Back to Main Menu")
        print("-" * 50)

        choice = input_string("  Enter choice (0-6): ")

        if choice == "1":
            display_products_table(products)
            input("\nPress Enter to continue...")

        elif choice == "2":
            print("\n--- Add New Product ---")
            new_id = input_string("  Enter Unique Product ID (e.g. P111): ").upper()
            if find_product_by_id(products, new_id):
                print(f"  [!] Error: Product with ID '{new_id}' already exists!")
                continue

            name = input_string("  Enter Product Name: ")
            category = input_string("  Enter Category: ")
            price = input_float(f"  Enter Unit Price ({CURRENCY}): ", min_val=0.01)
            stock = input_int("  Enter Initial Stock Quantity: ", min_val=0)
            threshold = input_int("  Enter Low-Stock Threshold: ", min_val=1)
            gst_rate = input_float("  Enter GST Rate % (e.g. 5, 12, 18): ", min_val=0.0, max_val=40.0)

            new_prod = {
                "id": new_id,
                "name": name,
                "category": category,
                "price": price,
                "stock": stock,
                "threshold": threshold,
                "gst_rate": gst_rate
            }
            products.append(new_prod)
            save_products(products)
            print(f"\n  [OK] Success: Product '{name}' [{new_id}] added to catalogue!")
            input("\nPress Enter to continue...")

        elif choice == "3":
            print("\n--- Update Product Price ---")
            p_id = input_string("  Enter Product ID to update: ").upper()
            prod = find_product_by_id(products, p_id)
            if not prod:
                print(f"  [!] Product '{p_id}' not found.")
                continue

            print(f"  Current Product: {prod['name']} | Current Price: {CURRENCY} {prod['price']:.2f}")
            new_price = input_float(f"  Enter New Price ({CURRENCY}): ", min_val=0.01)
            old_price = prod["price"]
            prod["price"] = new_price
            save_products(products)
            print(f"\n  [OK] Price updated for '{prod['name']}': {CURRENCY} {old_price:.2f} -> {CURRENCY} {new_price:.2f}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            print("\n--- Update Product Stock ---")
            p_id = input_string("  Enter Product ID: ").upper()
            prod = find_product_by_id(products, p_id)
            if not prod:
                print(f"  [!] Product '{p_id}' not found.")
                continue

            print(f"  Product: {prod['name']} | Current Stock: {prod['stock']} units")
            print("  Options: [1] Add to stock  [2] Set exact new stock count")
            sub_c = input_string("  Select option (1/2): ")
            if sub_c == "1":
                qty_to_add = input_int("  Enter units to add: ", min_val=1)
                prod["stock"] += qty_to_add
                print(f"\n  [OK] Added {qty_to_add} units. New Stock: {prod['stock']} units.")
            elif sub_c == "2":
                exact_qty = input_int("  Enter exact new stock: ", min_val=0)
                prod["stock"] = exact_qty
                print(f"\n  [OK] Stock count updated. New Stock: {prod['stock']} units.")
            else:
                print("  [!] Invalid selection.")
                continue

            save_products(products)
            input("\nPress Enter to continue...")

        elif choice == "5":
            print("\n--- Remove Product ---")
            p_id = input_string("  Enter Product ID to remove: ").upper()
            prod = find_product_by_id(products, p_id)
            if not prod:
                print(f"  [!] Product '{p_id}' not found.")
                continue

            confirm = input_string(f"  Are you sure you want to remove '{prod['name']}' ({p_id})? (y/n): ")
            if confirm.lower() == 'y':
                products = [p for p in products if p["id"].upper() != p_id]
                save_products(products)
                print(f"\n  [OK] Product '{prod['name']}' removed successfully.")
            else:
                print("  [i] Deletion cancelled.")
            input("\nPress Enter to continue...")

        elif choice == "6":
            menu_search_product()

        elif choice == "0":
            break
        else:
            print("  [!] Invalid choice. Please choose from 0 to 6.")


# ------------------------------------------------------------------------------
# SEARCH FEATURE
# ------------------------------------------------------------------------------
def menu_search_product():
    """Search catalogue by Product ID, Name, or Category."""
    products = load_products()
    print("\n" + "-" * 50)
    print("               SEARCH PRODUCTS")
    print("-" * 50)
    print("  [1] Search by Product Name")
    print("  [2] Search by Category")
    print("  [3] Search by Product ID")
    print("  [0] Back")
    print("-" * 50)

    choice = input_string("  Enter choice (0-3): ")
    if choice == "0":
        return

    query = input_string("  Enter search term: ").lower()
    matches = []

    if choice == "1":
        matches = [p for p in products if query in p["name"].lower()]
    elif choice == "2":
        matches = [p for p in products if query in p["category"].lower()]
    elif choice == "3":
        matches = [p for p in products if query in p["id"].lower()]
    else:
        print("  [!] Invalid search option.")
        return

    if matches:
        display_products_table(matches, title=f"SEARCH RESULTS FOR '{query.upper()}'")
    else:
        print(f"\n  [i] No products found matching '{query}'.")

    input("\nPress Enter to continue...")


# ------------------------------------------------------------------------------
# INVENTORY MANAGEMENT
# ------------------------------------------------------------------------------
def menu_inventory():
    """Inventory Management menu for stock inspection and restock."""
    while True:
        products = load_products()
        print("\n" + "-" * 50)
        print("           INVENTORY MANAGEMENT")
        print("-" * 50)
        print("  [1] View Complete Inventory Status")
        print("  [2] View Low-Stock & Out-of-Stock Alerts")
        print("  [3] Quick Restock Product")
        print("  [0] Back to Main Menu")
        print("-" * 50)

        choice = input_string("  Enter choice (0-3): ")

        if choice == "1":
            display_products_table(products, title="CURRENT INVENTORY LEVELS")
            input("\nPress Enter to continue...")

        elif choice == "2":
            alert_items = [p for p in products if p["stock"] <= p.get("threshold", 5)]
            if not alert_items:
                print("\n  [OK] Great! All products have healthy stock levels above threshold.")
            else:
                print("\n  [!] ATTENTION: The following products require restocking:")
                display_products_table(alert_items, title="INVENTORY ALERT LIST")
            input("\nPress Enter to continue...")

        elif choice == "3":
            print("\n--- Quick Restock ---")
            p_id = input_string("  Enter Product ID to restock: ").upper()
            prod = find_product_by_id(products, p_id)
            if not prod:
                print(f"  [!] Product '{p_id}' not found.")
                continue

            print(f"  Product: {prod['name']}")
            print(f"  Current Stock: {prod['stock']} | Low-Stock Threshold: {prod.get('threshold', 5)}")
            units = input_int("  Enter units to add to inventory: ", min_val=1)
            prod["stock"] += units
            save_products(products)
            print(f"\n  [OK] Restocked successfully! New Stock: {prod['stock']} units.")
            input("\nPress Enter to continue...")

        elif choice == "0":
            break
        else:
            print("  [!] Invalid choice. Please choose from 0 to 3.")


# ------------------------------------------------------------------------------
# SMART DISCOUNT & TAX ENGINE
# ------------------------------------------------------------------------------
def calculate_item_quantity_discount(price, qty):
    """
    Item-level quantity discount:
    - 10 or more units: 10% discount on that line item
    - 5 to 9 units: 5% discount on that line item
    - Below 5 units: 0% discount
    """
    subtotal = price * qty
    if qty >= 10:
        rate = 10.0
    elif qty >= 5:
        rate = 5.0
    else:
        rate = 0.0

    discount_amt = round(subtotal * (rate / 100.0), 2)
    return rate, discount_amt


def calculate_bill_tier_discount(net_subtotal):
    """
    Bill-value tiered discount applied on net subtotal:
    - Purchase >= 5000 : 15% discount
    - Purchase >= 3000 : 10% discount
    - Purchase >= 1000 : 5% discount
    - Below 1000       : 0% discount
    """
    if net_subtotal >= 5000:
        rate = 15.0
    elif net_subtotal >= 3000:
        rate = 10.0
    elif net_subtotal >= 1000:
        rate = 5.0
    else:
        rate = 0.0

    discount_amt = round(net_subtotal * (rate / 100.0), 2)
    return rate, discount_amt


# ------------------------------------------------------------------------------
# BILL GENERATION & CART WORKFLOW
# ------------------------------------------------------------------------------
def generate_bill_id():
    """Generate a unique human-readable invoice number based on date and counter."""
    bills = load_bills()
    today_str = datetime.date.today().strftime("%Y%m%d")
    today_bills = [b for b in bills if b.get("bill_no", "").startswith(f"BILL-{today_str}")]
    next_seq = len(today_bills) + 1
    return f"BILL-{today_str}-{next_seq:04d}"


def display_cart(cart):
    """Display current cart items in a structured table."""
    if not cart:
        print("\n  [i] Cart is currently empty.")
        return

    print("\n" + "-" * 78)
    print("                           CURRENT CART ITEMS")
    print("-" * 78)
    print(f"{'#':<3} {'ID':<6} {'Product Name':<28} {f'Price({CURRENCY})':>10} {'Qty':>5} {f'Subtotal({CURRENCY})':>13} {'GST%':>6}")
    print("-" * 78)

    for idx, item in enumerate(cart, start=1):
        item_sub = item["price"] * item["qty"]
        print(
            f"{idx:<3} "
            f"{item['id']:<6} "
            f"{item['name'][:27]:<28} "
            f"{item['price']:>10.2f} "
            f"{item['qty']:>5} "
            f"{item_sub:>13.2f} "
            f"{item['gst_rate']:>5.1f}%"
        )
    print("-" * 78)


def compute_bill_financials(cart):
    """
    Perform complete calculation:
    1. Line item subtotals and quantity discounts
    2. Net subtotal
    3. Bill-level discount (tiered)
    4. Proportional distribution of bill discount to compute line-level taxable amount
    5. GST calculation per item according to its individual GST rate
    6. Grand total
    """
    gross_subtotal = 0.0
    total_qty_discount = 0.0
    line_details = []

    # Step 1: Calculate item subtotals and item-level quantity discounts
    for item in cart:
        line_gross = round(item["price"] * item["qty"], 2)
        qty_disc_rate, qty_disc_amt = calculate_item_quantity_discount(item["price"], item["qty"])
        line_after_qty_disc = line_gross - qty_disc_amt

        gross_subtotal += line_gross
        total_qty_discount += qty_disc_amt

        line_details.append({
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "price": item["price"],
            "qty": item["qty"],
            "line_gross": line_gross,
            "qty_disc_rate": qty_disc_rate,
            "qty_disc_amt": qty_disc_amt,
            "line_after_qty_disc": line_after_qty_disc,
            "gst_rate": item["gst_rate"]
        })

    net_after_qty_disc = gross_subtotal - total_qty_discount

    # Step 2: Calculate bill-value tiered discount
    bill_disc_rate, bill_disc_amt = calculate_bill_tier_discount(net_after_qty_disc)
    total_discount = round(total_qty_discount + bill_disc_amt, 2)
    overall_taxable = round(gross_subtotal - total_discount, 2)

    # Step 3: Distribute bill discount proportionally to each item to compute exact GST
    total_gst = 0.0
    processed_items = []

    for line in line_details:
        if net_after_qty_disc > 0:
            prop_bill_disc = round(bill_disc_amt * (line["line_after_qty_disc"] / net_after_qty_disc), 2)
        else:
            prop_bill_disc = 0.0

        item_taxable = max(0.0, round(line["line_after_qty_disc"] - prop_bill_disc, 2))
        item_gst = round(item_taxable * (line["gst_rate"] / 100.0), 2)
        item_final_amount = round(item_taxable + item_gst, 2)

        total_gst += item_gst

        processed_items.append({
            "product_id": line["id"],
            "name": line["name"],
            "category": line["category"],
            "price": line["price"],
            "quantity": line["qty"],
            "subtotal": line["line_gross"],
            "item_discount": line["qty_disc_amt"],
            "bill_discount_share": prop_bill_disc,
            "taxable_amount": item_taxable,
            "gst_rate": line["gst_rate"],
            "gst_amount": item_gst,
            "item_total": item_final_amount
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


def print_receipt(bill_data):
    """Render and print a clean, professional retail receipt in the terminal."""
    print("\n" + "=" * 74)
    print("                            SMARTBILL")
    print("             SMART STORE BILLING & INVENTORY SYSTEM")
    print("             123 Tech Park Road, Silicon Corridor")
    print("                Phone: +91 98765 43210 | GSTIN: 29ABCDE1234F1Z5")
    print("=" * 74)
    print(f" Bill No  : {bill_data['bill_no']:<28} Date : {bill_data['date']}")
    print(f" Customer : {bill_data['customer_name']:<28} Time : {bill_data['time']}")
    print(f" Phone    : {bill_data['customer_phone']}")
    print("-" * 74)
    print(f" {'ID':<6} {'Item Description':<26} {'Qty':>4} {'Price':>8} {'GST%':>6} {f'Amount({CURRENCY})':>14}")
    print("-" * 74)

    for itm in bill_data["items"]:
        print(
            f" {itm['product_id']:<6} "
            f"{itm['name'][:25]:<26} "
            f"{itm['quantity']:>4} "
            f"{itm['price']:>8.2f} "
            f"{itm['gst_rate']:>5.1f}% "
            f"{itm['item_total']:>14.2f}"
        )

    print("-" * 74)
    print(f" {'Gross Subtotal':<46} : {CURRENCY} {bill_data['subtotal']:>10.2f}")

    q_disc = bill_data["discount_breakdown"].get("quantity_discount", 0.0)
    b_disc = bill_data["discount_breakdown"].get("bill_discount", 0.0)
    b_rate = bill_data["discount_breakdown"].get("bill_discount_percent", 0.0)

    if q_disc > 0:
        print(f" {'Quantity Bulk Discount':<46} : -{CURRENCY}{q_disc:>10.2f}")
    if b_disc > 0:
        print(f" {f'Store Offer ({b_rate:.0f}% off on bill)':<46} : -{CURRENCY}{b_disc:>10.2f}")

    print(f" {'Total Discount Given':<46} : -{CURRENCY}{bill_data['total_discount']:>10.2f}")
    print(f" {'Net Taxable Value':<46} : {CURRENCY} {bill_data['taxable_amount']:>10.2f}")
    print(f" {'Total GST Amount':<46} : {CURRENCY} {bill_data['total_gst']:>10.2f}")
    print("=" * 74)
    print(f" {'GRAND TOTAL':<46} : {CURRENCY} {bill_data['grand_total']:>10.2f}")
    print("=" * 74)
    print(f" Payment Mode : {bill_data['payment_mode']:<20}")
    print(f" Amount Paid  : {CURRENCY} {bill_data['amount_paid']:>8.2f}")
    if bill_data["payment_mode"] == "Cash":
        print(f" Change Due   : {CURRENCY} {bill_data['change']:>8.2f}")
    if bill_data.get("payment_ref"):
        print(f" Ref / Auth ID: {bill_data['payment_ref']}")
    print("=" * 74)
    print("                   Thank You for Shopping with SmartBill!")
    print("                        Visit Again & Have a Great Day!")
    print("=" * 74 + "\n")


def create_new_bill():
    """Interactive workflow to create a complete customer bill."""
    products = load_products()
    if not products:
        print("\n  [!] Product catalogue is empty. Please add products first.")
        return

    print("\n" + "=" * 50)
    print("            CREATE NEW CUSTOMER BILL")
    print("=" * 50)

    customer_name = input_string("  Enter Customer Name: ")
    customer_phone = input_phone("  Enter Customer Phone (10 digits): ")

    cart = []  # List of items: {"id", "name", "category", "price", "stock", "threshold", "gst_rate", "qty"}

    while True:
        display_cart(cart)
        print("\n  Cart Actions:")
        print("  [1] Add Product to Cart")
        print("  [2] Change Item Quantity")
        print("  [3] Remove Item from Cart")
        print("  [4] Quick View Product Catalogue")
        print("  [5] Proceed to Checkout & Payment")
        print("  [0] Cancel & Discard Bill")
        print("-" * 50)

        action = input_string("  Select action (0-5): ")

        if action == "1":
            print("\n--- Add Product ---")
            p_id = input_string("  Enter Product ID (e.g. P101): ").upper()
            prod = find_product_by_id(products, p_id)
            if not prod:
                print(f"  [!] Product '{p_id}' does not exist in catalogue.")
                continue

            available_stock = prod["stock"]
            in_cart_qty = sum(item["qty"] for item in cart if item["id"] == prod["id"])
            remaining_shelf_stock = available_stock - in_cart_qty

            if remaining_shelf_stock <= 0:
                print(f"  [!] OUT OF STOCK: All available units ({available_stock}) are already in cart or depleted.")
                continue

            print(f"  Found: {prod['name']} | Price: {CURRENCY} {prod['price']:.2f} | Available Stock: {remaining_shelf_stock}")
            if remaining_shelf_stock <= prod.get("threshold", 5):
                print(f"  [Warning: Stock is low! Only {remaining_shelf_stock} units left on shelf.]")

            qty = input_int(f"  Enter Quantity (1 to {remaining_shelf_stock}): ", min_val=1)
            if qty > remaining_shelf_stock:
                print(f"  [!] Insufficient stock! Cannot add {qty} units. Only {remaining_shelf_stock} available.")
                continue

            existing_item = next((item for item in cart if item["id"] == prod["id"]), None)
            if existing_item:
                existing_item["qty"] += qty
                print(f"  [OK] Updated '{prod['name']}' in cart. New Quantity: {existing_item['qty']}.")
            else:
                cart.append({
                    "id": prod["id"],
                    "name": prod["name"],
                    "category": prod["category"],
                    "price": prod["price"],
                    "gst_rate": prod["gst_rate"],
                    "threshold": prod.get("threshold", 5),
                    "total_stock": prod["stock"],
                    "qty": qty
                })
                print(f"  [OK] Added {qty}x '{prod['name']}' to cart.")

        elif action == "2":
            if not cart:
                print("  [!] Cart is empty.")
                continue
            display_cart(cart)
            item_num = input_int(f"  Enter Item # to modify quantity (1 to {len(cart)}): ", min_val=1, max_val=len(cart))
            target_item = cart[item_num - 1]
            prod = find_product_by_id(products, target_item["id"])
            max_allowed = prod["stock"]
            print(f"  Modifying: {target_item['name']} (Current Cart Qty: {target_item['qty']}, Store Stock: {max_allowed})")
            new_qty = input_int(f"  Enter New Quantity (1 to {max_allowed}): ", min_val=1, max_val=max_allowed)
            target_item["qty"] = new_qty
            print(f"  [OK] Quantity updated to {new_qty}.")

        elif action == "3":
            if not cart:
                print("  [!] Cart is empty.")
                continue
            display_cart(cart)
            item_num = input_int(f"  Enter Item # to remove (1 to {len(cart)}): ", min_val=1, max_val=len(cart))
            removed = cart.pop(item_num - 1)
            print(f"  [OK] Removed '{removed['name']}' from cart.")

        elif action == "4":
            display_products_table(products)

        elif action == "5":
            if not cart:
                print("  [!] Cannot checkout an empty cart. Please add items first.")
                continue

            financials = compute_bill_financials(cart)

            print("\n" + "=" * 50)
            print("                 BILL SUMMARY")
            print("=" * 50)
            print(f"  Gross Subtotal          : {CURRENCY} {financials['gross_subtotal']:.2f}")
            if financials["total_qty_discount"] > 0:
                print(f"  Quantity Discount       : -{CURRENCY} {financials['total_qty_discount']:.2f}")
            if financials["bill_disc_amt"] > 0:
                print(f"  Bill Offer ({financials['bill_disc_rate']:.0f}%)        : -{CURRENCY} {financials['bill_disc_amt']:.2f}")
            print(f"  Total Discount          : -{CURRENCY} {financials['total_discount']:.2f}")
            print(f"  Taxable Amount          : {CURRENCY} {financials['overall_taxable']:.2f}")
            print(f"  Total GST Amount        : {CURRENCY} {financials['total_gst']:.2f}")
            print("-" * 50)
            print(f"  GRAND TOTAL PAYABLE     : {CURRENCY} {financials['grand_total']:.2f}")
            print("=" * 50)

            confirm = input_string("  Confirm and proceed to payment? (y/n): ")
            if confirm.lower() != 'y':
                print("  [i] Returned to cart editing.")
                continue

            # Payment processing
            print("\n  Payment Modes:")
            print("  [1] Cash")
            print("  [2] UPI (GPay / PhonePe / Paytm / QR)")
            print("  [3] Card (Debit / Credit)")
            pay_choice = input_string("  Select payment mode (1-3): ")

            payment_mode = "Cash"
            amount_paid = financials["grand_total"]
            change_due = 0.0
            payment_ref = ""

            if pay_choice == "1":
                payment_mode = "Cash"
                while True:
                    cash_given = input_float(f"  Enter cash received (Minimum {CURRENCY} {financials['grand_total']:.2f}): ", min_val=0.0)
                    if cash_given < financials["grand_total"]:
                        shortage = financials["grand_total"] - cash_given
                        print(f"  [!] Insufficient cash! Short by {CURRENCY} {shortage:.2f}. Please collect full amount.")
                        continue
                    amount_paid = cash_given
                    change_due = round(cash_given - financials["grand_total"], 2)
                    print(f"  [OK] Cash Collected: {CURRENCY} {amount_paid:.2f} | Change to return: {CURRENCY} {change_due:.2f}")
                    break

            elif pay_choice == "2":
                payment_mode = "UPI"
                ref = input_string("  Enter UPI Transaction ID (or press Enter for auto-ref): ", allow_empty=True)
                if not ref:
                    ref = f"UPI-{datetime.datetime.now().strftime('%H%M%S%f')[:10]}"
                payment_ref = ref
                print(f"  [OK] UPI payment confirmed with Ref: {payment_ref}")

            elif pay_choice == "3":
                payment_mode = "Card"
                card_last4 = input_string("  Enter last 4 digits of card (or press Enter for auto-auth): ", allow_empty=True)
                if card_last4 and len(card_last4) == 4 and card_last4.isdigit():
                    payment_ref = f"CARD-XXXX-XXXX-XXXX-{card_last4}"
                else:
                    payment_ref = f"CARD-AUTH-{datetime.datetime.now().strftime('%H%M%S')}"
                print(f"  [OK] Card payment approved with Auth: {payment_ref}")

            else:
                print("  [!] Invalid choice, defaulting to Cash exact amount.")
                payment_mode = "Cash"
                amount_paid = financials["grand_total"]
                change_due = 0.0

            # Deduct stock from inventory
            for item in cart:
                prod = find_product_by_id(products, item["id"])
                if prod:
                    prod["stock"] = max(0, prod["stock"] - item["qty"])
            save_products(products)

            # Build final bill record
            now = datetime.datetime.now()
            bill_record = {
                "bill_no": generate_bill_id(),
                "date": now.strftime("%d/%m/%Y"),
                "time": now.strftime("%H:%M:%S"),
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "items": financials["items"],
                "subtotal": financials["gross_subtotal"],
                "discount_breakdown": {
                    "quantity_discount": financials["total_qty_discount"],
                    "bill_discount": financials["bill_disc_amt"],
                    "bill_discount_percent": financials["bill_disc_rate"],
                    "total_discount": financials["total_discount"]
                },
                "total_discount": financials["total_discount"],
                "taxable_amount": financials["overall_taxable"],
                "total_gst": financials["total_gst"],
                "grand_total": financials["grand_total"],
                "payment_mode": payment_mode,
                "amount_paid": amount_paid,
                "change": change_due,
                "payment_ref": payment_ref
            }

            # Save bill to persistent history
            bills = load_bills()
            bills.append(bill_record)
            save_bills(bills)

            # Display printed receipt
            print_receipt(bill_record)

            # Stock warning alerts for cashier awareness
            print("  --- Inventory Post-Sale Alerts ---")
            alerts_triggered = False
            for item in cart:
                updated_prod = find_product_by_id(products, item["id"])
                if updated_prod:
                    rem = updated_prod["stock"]
                    thresh = updated_prod.get("threshold", 5)
                    if rem == 0:
                        print(f"  [!] ALERT: '{updated_prod['name']}' is now OUT OF STOCK!")
                        alerts_triggered = True
                    elif rem <= thresh:
                        print(f"  [!] WARNING: '{updated_prod['name']}' is LOW ON STOCK ({rem} units remaining, threshold: {thresh})")
                        alerts_triggered = True
            if not alerts_triggered:
                print("  [OK] All purchased products remain at healthy stock levels.")

            input("\nPress Enter to return to Main Menu...")
            break

        elif action == "0":
            confirm_cancel = input_string("  Are you sure you want to cancel and discard this bill? (y/n): ")
            if confirm_cancel.lower() == 'y':
                print("  [i] Bill cancelled. Stock was not modified.")
                break
        else:
            print("  [!] Invalid action. Please enter 0 to 5.")


# ------------------------------------------------------------------------------
# BILL HISTORY & REPRINT
# ------------------------------------------------------------------------------
def menu_bill_history():
    """Browse historical bills and reprint formatted receipts."""
    while True:
        bills = load_bills()
        print("\n" + "-" * 50)
        print("                 BILL HISTORY")
        print("-" * 50)
        print("  [1] View All Past Bills (Summary Table)")
        print("  [2] Search & Reprint Bill by Bill Number")
        print("  [3] Search Bills by Customer Phone")
        print("  [0] Back to Main Menu")
        print("-" * 50)

        choice = input_string("  Enter choice (0-3): ")

        if choice == "1":
            if not bills:
                print("\n  [i] No past bills found in the system.")
                input("\nPress Enter to continue...")
                continue

            print("\n" + "=" * 80)
            print("                             ALL COMPLETED BILLS")
            print("=" * 80)
            print(f"{'Bill No':<20} {'Date':<12} {'Customer':<20} {'Items':>5} {f'Grand Total({CURRENCY})':>16} {'Mode':<6}")
            print("-" * 80)
            for b in bills:
                item_count = sum(i["quantity"] for i in b.get("items", []))
                print(
                    f"{b['bill_no']:<20} "
                    f"{b['date']:<12} "
                    f"{b['customer_name'][:19]:<20} "
                    f"{item_count:>5} "
                    f"{b['grand_total']:>16.2f} "
                    f"{b['payment_mode']:<6}"
                )
            print("=" * 80)
            input("\nPress Enter to continue...")

        elif choice == "2":
            if not bills:
                print("\n  [i] No bills available.")
                continue
            b_id = input_string("  Enter Bill Number (e.g. BILL-20260908-0001): ").upper()
            found = next((b for b in bills if b["bill_no"].upper() == b_id), None)
            if found:
                print_receipt(found)
            else:
                print(f"  [!] Bill '{b_id}' not found.")
            input("\nPress Enter to continue...")

        elif choice == "3":
            if not bills:
                print("\n  [i] No bills available.")
                continue
            phone = input_string("  Enter 10-digit Customer Phone: ")
            matches = [b for b in bills if phone in b.get("customer_phone", "")]
            if not matches:
                print(f"  [i] No bills found for phone '{phone}'.")
            else:
                print(f"\n  Found {len(matches)} bill(s) for customer phone '{phone}':")
                for m in matches:
                    print(f"  - Bill No: {m['bill_no']} | Date: {m['date']} | Total: {CURRENCY} {m['grand_total']:.2f}")
                reprint_one = input_string("  Enter Bill No to view full receipt (or press Enter to skip): ", allow_empty=True).upper()
                if reprint_one:
                    selected = next((b for b in matches if b["bill_no"].upper() == reprint_one), None)
                    if selected:
                        print_receipt(selected)
                    else:
                        print(f"  [!] Bill '{reprint_one}' not in matched list.")
            input("\nPress Enter to continue...")

        elif choice == "0":
            break
        else:
            print("  [!] Invalid choice. Please choose from 0 to 3.")


# ------------------------------------------------------------------------------
# SALES SUMMARY & ANALYTICS
# ------------------------------------------------------------------------------
def menu_sales_summary():
    """Compute and display daily / overall business performance summary."""
    bills = load_bills()
    print("\n" + "=" * 65)
    print("                    STORE SALES SUMMARY & ANALYTICS")
    print("=" * 65)

    if not bills:
        print("  [i] No sales data available yet. Generate bills to view analytics.")
        print("=" * 65)
        input("\nPress Enter to continue...")
        return

    total_bills = len(bills)
    total_revenue = sum(b.get("grand_total", 0.0) for b in bills)
    total_gst = sum(b.get("total_gst", 0.0) for b in bills)
    total_discounts = sum(b.get("total_discount", 0.0) for b in bills)
    total_gross = sum(b.get("subtotal", 0.0) for b in bills)

    total_units_sold = 0
    product_sales_volume = {}  # {prod_name: total_qty}
    product_sales_revenue = {}  # {prod_name: total_revenue}

    payment_counts = {"Cash": 0, "UPI": 0, "Card": 0}
    payment_amounts = {"Cash": 0.0, "UPI": 0.0, "Card": 0.0}

    for b in bills:
        mode = b.get("payment_mode", "Cash")
        payment_counts[mode] = payment_counts.get(mode, 0) + 1
        payment_amounts[mode] = payment_amounts.get(mode, 0.0) + b.get("grand_total", 0.0)

        for item in b.get("items", []):
            q = item.get("quantity", 0)
            name = item.get("name", "Unknown")
            tot = item.get("item_total", 0.0)

            total_units_sold += q
            product_sales_volume[name] = product_sales_volume.get(name, 0) + q
            product_sales_revenue[name] = product_sales_revenue.get(name, 0.0) + tot

    avg_bill_value = total_revenue / total_bills if total_bills > 0 else 0.0

    print(f"  Total Invoices Generated  : {total_bills}")
    print(f"  Total Products / Units Sold: {total_units_sold} units")
    print(f"  Gross Sales Subtotal      : {CURRENCY} {total_gross:>10.2f}")
    print(f"  Total Discounts Given     : {CURRENCY} {total_discounts:>10.2f}")
    print(f"  Total GST Collected       : {CURRENCY} {total_gst:>10.2f}")
    print("-" * 65)
    print(f"  NET TOTAL REVENUE         : {CURRENCY} {total_revenue:>10.2f}")
    print(f"  Average Basket Value      : {CURRENCY} {avg_bill_value:>10.2f}")
    print("-" * 65)

    print("  Payment Mode Distribution:")
    for mode in ["Cash", "UPI", "Card"]:
        cnt = payment_counts.get(mode, 0)
        amt = payment_amounts.get(mode, 0.0)
        pct = (amt / total_revenue * 100) if total_revenue > 0 else 0.0
        print(f"    - {mode:<5} : {cnt:>3} bills | Total: {CURRENCY} {amt:>9.2f} ({pct:>5.1f}%)")

    print("-" * 65)
    print("  Top Selling Products (by Volume):")
    if product_sales_volume:
        sorted_prods = sorted(product_sales_volume.items(), key=lambda x: x[1], reverse=True)[:3]
        for rank, (name, qty) in enumerate(sorted_prods, start=1):
            rev = product_sales_revenue.get(name, 0.0)
            print(f"    {rank}. {name:<30} -> {qty:>3} units ({CURRENCY} {rev:.2f})")
    else:
        print("    None recorded.")

    print("=" * 65)
    input("\nPress Enter to continue...")


# ------------------------------------------------------------------------------
# MAIN APPLICATION CONTROLLER
# ------------------------------------------------------------------------------
def main():
    """Main application loop with clean, user-friendly console UI."""
    initialize_data_files()

    while True:
        print("\n" + "=" * 54)
        print("                 SMARTBILL SYSTEM")
        print("     Smart Store Billing & Inventory Management")
        print("=" * 54)
        print("  [1] Create New Bill")
        print("  [2] Product Catalogue (View / Add / Edit / Remove)")
        print("  [3] Manage Inventory (Stock levels & Restocking)")
        print("  [4] Bill History (View Past Invoices & Reprint)")
        print("  [5] Sales Summary & Business Analytics")
        print("  [6] Search Product")
        print("  [7] Exit")
        print("=" * 54)

        choice = input_string("  Enter choice (1-7): ")

        if choice == "1":
            create_new_bill()
        elif choice == "2":
            menu_product_catalogue()
        elif choice == "3":
            menu_inventory()
        elif choice == "4":
            menu_bill_history()
        elif choice == "5":
            menu_sales_summary()
        elif choice == "6":
            menu_search_product()
        elif choice == "7":
            print("\n  ========================================================")
            print("   Thank you for using SmartBill! Goodbye and have a great day.")
            print("  ========================================================\n")
            break
        else:
            print("  [!] Invalid selection. Please enter a digit from 1 to 7.")


if __name__ == "__main__":
    main()
