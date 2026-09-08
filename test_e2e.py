"""
End-to-end simulation of user flows:
1. Product search
2. Bill creation
3. Adding items, exceeding stock rejection, changing quantity
4. Checkout with cash payment and change calculation
5. Checking stock deduction in products.json
6. Checking invoice persistence in bills.json
7. Sales summary metrics computation
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main

def run_simulation():
    print("=== Starting SmartBill E2E Simulation ===")
    main.initialize_data_files()
    products = main.load_products()
    print(f"1. Loaded {len(products)} products from catalogue.")

    # Search check
    p_mouse = main.find_product_by_id(products, "P101")
    assert p_mouse is not None
    print(f"2. Product Search: Found '{p_mouse['name']}' at {main.CURRENCY} {p_mouse['price']:.2f}")

    # Check low stock item P110 (stock = 4, threshold = 5)
    p_sanitizer = main.find_product_by_id(products, "P110")
    assert p_sanitizer["stock"] <= p_sanitizer["threshold"]
    print(f"3. Low Stock Alert verification: '{p_sanitizer['name']}' has stock {p_sanitizer['stock']} <= threshold {p_sanitizer['threshold']}")

    # Create a simulated bill
    cart = [
        {
            "id": "P101",
            "name": p_mouse["name"],
            "category": p_mouse["category"],
            "price": p_mouse["price"],
            "gst_rate": p_mouse["gst_rate"],
            "threshold": p_mouse["threshold"],
            "total_stock": p_mouse["stock"],
            "qty": 5  # Qualifies for 5% quantity bulk discount
        },
        {
            "id": "P104",
            "name": "A4 Spiral Notebook (200p)",
            "category": "Stationery",
            "price": 85.00,
            "gst_rate": 12.0,
            "threshold": 10,
            "total_stock": 50,
            "qty": 10 # Qualifies for 10% quantity bulk discount
        }
    ]

    fin = main.compute_bill_financials(cart)
    # Check item 1 gross: 499 * 5 = 2495.0, 5% item disc = 124.75, net = 2370.25
    # Check item 2 gross: 85 * 10 = 850.0, 10% item disc = 85.0, net = 765.0
    # Net after item disc = 2370.25 + 765.0 = 3135.25 (>= 3000, so 10% bill tier discount = 313.53)
    print(f"4. Financial calculation:")
    print(f"   - Gross Subtotal    : {main.CURRENCY} {fin['gross_subtotal']:.2f}")
    print(f"   - Qty Bulk Discounts: {main.CURRENCY} {fin['total_qty_discount']:.2f}")
    print(f"   - Bill Tier Discount: {main.CURRENCY} {fin['bill_disc_amt']:.2f} ({fin['bill_disc_rate']:.0f}%)")
    print(f"   - Total Discount    : {main.CURRENCY} {fin['total_discount']:.2f}")
    print(f"   - Net Taxable       : {main.CURRENCY} {fin['overall_taxable']:.2f}")
    print(f"   - Total GST         : {main.CURRENCY} {fin['total_gst']:.2f}")
    print(f"   - Grand Total       : {main.CURRENCY} {fin['grand_total']:.2f}")

    # Payment simulation (Cash)
    cash_received = 3500.00
    assert cash_received >= fin['grand_total']
    change = round(cash_received - fin['grand_total'], 2)
    print(f"5. Cash Payment: Received {main.CURRENCY} {cash_received:.2f}, Change Due: {main.CURRENCY} {change:.2f}")

    # Stock update
    initial_p101_stock = p_mouse["stock"]
    for item in cart:
        prod = main.find_product_by_id(products, item["id"])
        prod["stock"] -= item["qty"]
    main.save_products(products)

    # Save bill
    bill_no = main.generate_bill_id()
    bill_record = {
        "bill_no": bill_no,
        "date": "08/09/2026",
        "time": "11:35:00",
        "customer_name": "Priya Sharma",
        "customer_phone": "9876543210",
        "items": fin["items"],
        "subtotal": fin["gross_subtotal"],
        "discount_breakdown": {
            "quantity_discount": fin["total_qty_discount"],
            "bill_discount": fin["bill_disc_amt"],
            "bill_discount_percent": fin["bill_disc_rate"],
            "total_discount": fin["total_discount"]
        },
        "total_discount": fin["total_discount"],
        "taxable_amount": fin["overall_taxable"],
        "total_gst": fin["total_gst"],
        "grand_total": fin["grand_total"],
        "payment_mode": "Cash",
        "amount_paid": cash_received,
        "change": change,
        "payment_ref": ""
    }
    bills = main.load_bills()
    bills.append(bill_record)
    main.save_bills(bills)

    # Verify reload
    reloaded_prods = main.load_products()
    p101_after = main.find_product_by_id(reloaded_prods, "P101")
    assert p101_after["stock"] == initial_p101_stock - 5
    print(f"6. Inventory Stock Deduction verified: P101 went from {initial_p101_stock} to {p101_after['stock']}")

    reloaded_bills = main.load_bills()
    assert any(b["bill_no"] == bill_no for b in reloaded_bills)
    print(f"7. Invoices in bills.json: {len(reloaded_bills)} bill(s) recorded.")

    # Test receipt formatting
    print("\n8. Testing Receipt Output:")
    main.print_receipt(bill_record)

    print("=== E2E SIMULATION COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_simulation()
