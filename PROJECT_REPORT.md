# JAIN (Deemed-to-be University)
### Faculty of Engineering and Technology
### School of Computer Science and Engineering
#### B. Tech CSE — Python Programming Mini Project Report

---

## Project Metadata

| Field | Details |
|---|---|
| **Name** | J S Rahul |
| **USN** | 25BTRPW048 |
| **Class/Section** | CSE-PWC-A |
| **Subject Name** | Python Programming |
| **Faculty Name** | Ms. Sujithra G |
| **Date of Submission** | 10/09/2026 |
| **Project Topic** | SmartBill – Smart Store Billing and Inventory Management System |
| **GitHub Link** | [https://github.com/JSRAHUL/SmartBIll](https://github.com/JSRAHUL/SmartBIll) |

---

## Table of Content

| S.No | Topic | Page No |
|---|---|---|
| 1 | Introduction | 3 |
| 2 | Problem Statement | 3 |
| 3 | Objectives | 3 |
| 4 | Project Description | 4 |
| 5 | Concepts Used in the Program | 4–5 |
| 6 | Algorithm | 5 |
| 7 | Flow Chart | 6 |
| 8 | Python Program | 7–9 |
| 9 | Output | 10 |
| 10 | Conclusion | 11 |

---

## 1. Introduction

In modern retail environments, efficient point-of-sale operations and dependable inventory control are essential computational requirements. Manual invoicing and hand calculations are notoriously prone to errors, often resulting in inaccurate tax applications, arithmetic mistakes, and inventory discrepancies that lead to overselling or stock depletion. To resolve these challenges, **SmartBill** is designed and implemented as an intelligent, automated retail billing and inventory management solution developed in Python.

The application integrates product cataloguing, shopping cart management, automatic multi-tiered discounting, multi-slab Goods and Services Tax (GST) computation, payment recording, and real-time inventory synchronization. By utilizing modular programming and persistent data storage (JSON and SQLite), the system establishes a clean separation of concerns between computational business logic, data persistence, and user interfaces.

Defensive programming principles and exception handling are embedded throughout the codebase. The application catches invalid inputs, prevents negative numbers, enforces stock boundaries, and validates customer mobile numbers. These design choices illustrate how core computer science concepts can be synthesized into an industry-grade software utility.

---

## 2. Problem Statement

Design and develop a Bill Generator application using Python that generates a customer bill for purchased products. The program should allow users to enter product details, quantity, and price, calculate the total amount, apply GST (if applicable), and display a formatted bill. The system must prevent negative stock, support item-level and bill-value discounts, handle multiple payment methods, and maintain persistent historical records.

---

## 3. Objectives

* To develop a modular and interactive billing application using Python.
* To maintain a persistent product catalogue containing product ID, name, category, price, stock, and GST rate.
* To automatically retrieve product details and prices from the catalogue to eliminate manual cashier pricing errors.
* To implement dual-tier discounts: item-level bulk quantity discounts and overall bill-value tiered discounts.
* To calculate statutory GST accurately across varying tax slabs (5%, 12%, 18%) post-discount on the net taxable amount.
* To implement real-time inventory synchronization by automatically decrementing stock upon successful payment.
* To validate stock availability before purchase and prevent negative stock or overselling.
* To calculate change due for cash payments and log digital payment methods (UPI, Card).
* To record transaction history persistently and generate daily sales summaries and business analytics.

---

## 4. Project Description

**SmartBill** is organized into modular Python components. Upon startup, the system loads existing inventory and transaction ledgers from persistent storage. If the system is initialized for the first time, it automatically bootstraps the database with realistic sample items across multiple categories (Electronics, Stationery, Groceries, Beverages, Personal Care).

The cashier interacts with an organized menu containing seven core modules: Create New Bill, Product Catalogue, Manage Inventory, Bill History, Sales Summary, Search Product, and Exit. During checkout, customer identification is captured and an invoice identifier with timestamps is generated.

When products are added to the cart, the system checks on-hand inventory, validates quantity limits, and computes line subtotals. At checkout, the engine evaluates item quantity discounts alongside bill-value store offers, apportions discounts proportionally, calculates category GST, manages payment tenders with change calculation, updates stock atomically, and prints a formatted receipt.

---

## 5. Concepts Used in the Program

* **Functions**: Modular architecture comprising 24 single-responsibility functions (e.g., `compute_bill_financials()`, `calculate_item_quantity_discount()`, `print_receipt()`).
* **Conditional Statements**: `if`, `elif`, and `else` branching for discount tiers, tax slabs, payment verification, and stock boundary checks.
* **Loops**: `while` loops for menu navigation and validation retries; `for` loops for cart iterations and financial aggregations.
* **Exception Handling**: `try-except` blocks catching `ValueError` during user input and handling `IOError` / `JSONDecodeError` during file operations.
* **Data Structures (Lists & Dictionaries)**: Dictionaries represent structured product models and invoice objects; lists hold cart items and catalogue records.
* **Arithmetic & Financial Operators**: Precision floating-point calculations for subtotals, percentage discounts, taxable bases, and change due.
* **String Formatting**: Formatted strings (f-strings) with width and precision specifiers (`{price:>10.2f}`) ensuring receipt alignment.
* **File Handling & Relational Persistence**: Built-in `json` and `sqlite3` modules provide data persistence across restarts.
* **Date & Time Module**: Standard `datetime` library powers timestamps and sequential invoice generation (`BILL-YYYYMMDD-XXXX`).
* **Defensive Validation**: Guards against negative numbers, overselling, non-numeric inputs, and invalid phone numbers.

---

## 6. Algorithm

1. Start the program and initialize data persistence files (`products.json`, `bills.json`, and `database.db`).
2. Display the SmartBill Main Menu (1: Create Bill, 2: Catalogue, 3: Inventory, 4: History, 5: Sales Summary, 6: Search, 7: Exit).
3. Read and validate the cashier's selection.
4. **If Create New Bill is selected:**
   - Prompt for customer name and 10-digit mobile number.
   - Generate unique bill number (`BILL-YYYYMMDD-XXXX`), date, and time.
   - Loop for adding products: read Product ID, retrieve price and stock.
   - Validate quantity: `requested_quantity <= available_stock`.
   - Compute item subtotal and add to active cart.
   - On checkout, compute item quantity discounts and bill-value store offer.
   - Distribute bill discounts proportionally across items to obtain net taxable values.
   - Apply product-specific GST rates (5%, 12%, 18%) to compute total GST.
   - Calculate Grand Total = Net Taxable Amount + Total GST.
   - Select payment mode (Cash, UPI, Card). If Cash, compute `Change Due = Tender - Grand Total`.
   - Atomically decrement purchased quantities from inventory.
   - Save invoice to persistent history and output formatted receipt.
5. **If Product Catalogue is selected:** Provide CRUD operations (View, Add, Edit, Delete).
6. **If Manage Inventory is selected:** Display stock levels, highlight low-stock items (`stock <= threshold`), and permit restocking.
7. **If Bill History is selected:** Browse past transactions and reprint invoices.
8. **If Sales Summary is selected:** Display aggregated revenue, total GST, total discounts, and top-selling products.
9. **If Search Product is selected:** Perform case-insensitive substring search by ID, name, or category.
10. **If Exit is selected:** Terminate session safely.

---

## 7. Flow Chart

```
                        +--------------------+
                        |       START        |
                        +--------------------+
                                  |
                                  v
                        +--------------------+
                        |  Initialize Data   |
                        | (Products & Bills) |
                        +--------------------+
                                  |
                                  v
+---------------------> +--------------------+
|                       | Display Main Menu  |
|                       |   (Options 1-7)    |
|                       +--------------------+
|                                 |
|                                 v
|                       +--------------------+
|                       |  Read User Choice  |
|                       +--------------------+
|                                 |
|       +-------------------------+-------------------------+
|       |                         |                         |
|       v                         v                         v
|  [Choice 1: Billing]     [Choice 2-6: Admin]       [Choice 7: Exit]
|       |                         |                         |
|       v                         v                         v
| Customer Info & Cart      Catalogue/Inventory/    +---------------+
| Validate Stock Levels     History/Reports Search  |      END      |
| Dual-Tier Discounts             |                 +---------------+
| Multi-Slab GST (5/12/18)        |
| Payment & Change Due            |
| Deduct Stock & Print            |
|       |                         |
|       +-------------------------+
|                   |
+-------------------+ (Return to Menu)
```

---

## 8. Python Program

*(Refer to `app.py` and `main.py` in the project repository for full implementation).*

```python
# Sample Core Calculation Logic from SmartBill
def compute_bill_financials(cart):
    gross_subtotal = sum(item["price"] * item["qty"] for item in cart)
    total_qty_discount = 0.0

    for item in cart:
        qty = item["qty"]
        rate = 10.0 if qty >= 10 else (5.0 if qty >= 5 else 0.0)
        total_qty_discount += round(item["price"] * qty * (rate / 100.0), 2)

    net_after_qty = gross_subtotal - total_qty_discount
    bill_rate = 15.0 if net_after_qty >= 5000 else (10.0 if net_after_qty >= 3000 else (5.0 if net_after_qty >= 1000 else 0.0))
    bill_disc_amt = round(net_after_qty * (bill_rate / 100.0), 2)
    total_discount = round(total_qty_discount + bill_disc_amt, 2)
    overall_taxable = round(gross_subtotal - total_discount, 2)

    total_gst = 0.0
    for item in cart:
        share = round(bill_disc_amt * ((item["price"] * item["qty"]) / gross_subtotal), 2) if gross_subtotal > 0 else 0.0
        taxable = max(0.0, (item["price"] * item["qty"]) - share)
        total_gst += round(taxable * (item["gst_rate"] / 100.0), 2)

    grand_total = round(overall_taxable + total_gst, 2)
    return {
        "subtotal": gross_subtotal,
        "discount": total_discount,
        "taxable": overall_taxable,
        "gst": round(total_gst, 2),
        "grand_total": grand_total
    }
```

---

## 9. Output

### Sample Customer Receipt

```text
==========================================================================
                            SMARTBILL
             SMART STORE BILLING & INVENTORY SYSTEM
             123 College Road, Silicon Corridor | Phone: +91 98765 43210
==========================================================================
 Bill No  : BILL-20260908-0001           Date : 10/09/2026
 Customer : Priya Sharma                 Time : 11:35:00
 Phone    : 9876543210
--------------------------------------------------------------------------
 ID     Item Description            Qty    Price   GST%    Amount(Rs.)
--------------------------------------------------------------------------
 P101   Wireless Optical Mouse        5   499.00  18.0%        2517.20
 P104   A4 Spiral Notebook (200p)    10    85.00  12.0%         771.12
--------------------------------------------------------------------------
 Gross Subtotal                                 : Rs.    3345.00
 Quantity Bulk Discount                         : -Rs.    209.75
 Store Offer (10% off on bill)                  : -Rs.    313.53
 Total Discount Given                           : -Rs.    523.28
 Net Taxable Value                              : Rs.    2821.72
 Total GST Amount                               : Rs.     466.60
==========================================================================
 GRAND TOTAL                                    : Rs.    3288.32
==========================================================================
 Payment Mode : Cash                
 Amount Paid  : Rs.  3500.00
 Change Due   : Rs.   211.68
==========================================================================
                   Thank You for Shopping with SmartBill!
==========================================================================
```

---

## 10. Conclusion

The **SmartBill – Smart Store Billing and Inventory Management System** successfully fulfills the academic objective of designing and developing an intelligent, robust, and real-world billing application in Python. Moving far beyond a basic calculator, the system demonstrates how automated store operations can eliminate manual pricing mistakes, enforce inventory constraints, and ensure statutory tax compliance.

The project highlights key Python programming principles including user-defined modular functions, exception handling, nested decision structures, persistent data serialization using JSON and SQLite, defensive input validation, and professional string formatting. The implementation of item-level bulk discounts alongside basket-value store offers provides a realistic commercial experience.

Real-time stock synchronization guarantees that shelf inventory automatically decrements upon successful checkout, preventing negative stock and providing early low-stock warnings to store managers. The application operates across both a fast command-line terminal and a modern browser-based web dashboard.

Overall, the project demonstrates how foundational programming techniques taught in the computer science curriculum can be synthesized to create an industry-relevant software product. Future enhancements can expand the platform with hardware barcode scanners, cloud database synchronization, and digital receipt dispatch via SMS or email.

---

**Project Topic:** SmartBill – Smart Store Billing and Inventory Management System  
**Student:** J S Rahul  
**USN:** 25BTRPW048  
**Class/Section:** CSE-PWC-A  
**Faculty Guide:** Ms. Sujithra G  
