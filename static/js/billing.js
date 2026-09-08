/**
 * SmartBill - POS Billing Terminal JavaScript
 */

let cart = [];
let currentFinancials = {
  gross_subtotal: 0.0,
  total_qty_discount: 0.0,
  bill_disc_amt: 0.0,
  bill_disc_rate: 0.0,
  total_discount: 0.0,
  overall_taxable: 0.0,
  total_gst: 0.0,
  grand_total: 0.0,
  items: []
};
let selectedPaymentMode = "Cash";

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("posSearchInput");
  const searchDropdown = document.getElementById("searchDropdown");
  const categoryFilter = document.getElementById("posCategoryFilter");
  const cashGivenInput = document.getElementById("cashGivenInput");

  let debounceTimer;

  // Search input with debounce
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      const cat = categoryFilter ? categoryFilter.value : "";

      if (query.length === 0 && !cat) {
        if (searchDropdown) searchDropdown.style.display = "none";
        return;
      }

      debounceTimer = setTimeout(() => {
        fetchProducts(query, cat);
      }, 200);
    });

    searchInput.addEventListener("focus", () => {
      const query = searchInput.value.trim();
      const cat = categoryFilter ? categoryFilter.value : "";
      fetchProducts(query, cat);
    });
  }

  if (categoryFilter) {
    categoryFilter.addEventListener("change", () => {
      const query = searchInput ? searchInput.value.trim() : "";
      fetchProducts(query, categoryFilter.value);
    });
  }

  // Close dropdown on click outside
  document.addEventListener("click", (e) => {
    if (searchDropdown && !e.target.closest(".pos-search-wrapper")) {
      searchDropdown.style.display = "none";
    }
  });

  // Payment Mode selection
  document.querySelectorAll(".payment-mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".payment-mode-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedPaymentMode = btn.dataset.mode;

      const cashGroup = document.getElementById("cashInputGroup");
      const upiGroup = document.getElementById("upiInputGroup");
      const cardGroup = document.getElementById("cardInputGroup");

      if (cashGroup) cashGroup.style.display = selectedPaymentMode === "Cash" ? "block" : "none";
      if (upiGroup) upiGroup.style.display = selectedPaymentMode === "UPI" ? "block" : "none";
      if (cardGroup) cardGroup.style.display = selectedPaymentMode === "Card" ? "block" : "none";

      updateChangeDue();
    });
  });

  // Cash Received calculation
  if (cashGivenInput) {
    cashGivenInput.addEventListener("input", updateChangeDue);
  }

  // Checkout button
  const checkoutBtn = document.getElementById("btnCheckout");
  if (checkoutBtn) {
    checkoutBtn.addEventListener("click", handleCheckout);
  }

  // Clear cart button
  const clearBtn = document.getElementById("btnClearCart");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (cart.length > 0 && confirm("Are you sure you want to clear the cart?")) {
        cart = [];
        renderCart();
      }
    });
  }
});

function fetchProducts(query, category) {
  const searchDropdown = document.getElementById("searchDropdown");
  if (!searchDropdown) return;

  fetch(`/api/products/search?q=${encodeURIComponent(query)}&cat=${encodeURIComponent(category)}`)
    .then((res) => res.json())
    .then((data) => {
      const products = data.products || [];
      if (products.length === 0) {
        searchDropdown.innerHTML = `<div class="p-3 text-muted text-center" style="padding: 12px; font-size: 0.88rem; color: #64748b;">No matching products found.</div>`;
        searchDropdown.style.display = "block";
        return;
      }

      let html = "";
      products.forEach((p) => {
        html += `
          <div class="search-item" onclick='addToCart(${JSON.stringify(p)})'>
            <div>
              <strong style="font-size: 0.92rem;">${escapeHtml(p.name)}</strong>
              <div style="font-size: 0.76rem; color: #64748b;">
                <span class="badge badge-neutral">${p.product_code}</span> ${p.category} | GST: ${p.gst_rate}%
              </div>
            </div>
            <div style="text-align: right;">
              <div style="font-weight: 700; color: #4f46e5;">Rs. ${p.selling_price.toFixed(2)}</div>
              <div style="font-size: 0.76rem; color: ${p.stock <= p.threshold ? '#ef4444' : '#10b981'};">
                Stock: ${p.stock}
              </div>
            </div>
          </div>
        `;
      });
      searchDropdown.innerHTML = html;
      searchDropdown.style.display = "block";
    })
    .catch((err) => console.error("Search error:", err));
}

function addToCart(product) {
  const existing = cart.find((item) => item.product_id === product.id);

  if (existing) {
    if (existing.quantity + 1 > product.stock) {
      alert(`Cannot add more units. Available shelf stock: ${product.stock}`);
      return;
    }
    existing.quantity += 1;
  } else {
    if (product.stock < 1) {
      alert("Product is out of stock!");
      return;
    }
    cart.push({
      product_id: product.id,
      product_code: product.product_code,
      name: product.name,
      category: product.category,
      selling_price: product.selling_price,
      cost_price: product.cost_price,
      gst_rate: product.gst_rate,
      stock: product.stock,
      quantity: 1
    });
  }

  const dropdown = document.getElementById("searchDropdown");
  if (dropdown) dropdown.style.display = "none";

  const searchInput = document.getElementById("posSearchInput");
  if (searchInput) searchInput.value = "";

  renderCart();
}

function updateQuantity(productId, delta) {
  const item = cart.find((i) => i.product_id === productId);
  if (!item) return;

  const newQty = item.quantity + delta;
  if (newQty <= 0) {
    removeFromCart(productId);
    return;
  }

  if (newQty > item.stock) {
    alert(`Only ${item.stock} units available in inventory.`);
    return;
  }

  item.quantity = newQty;
  renderCart();
}

function removeFromCart(productId) {
  cart = cart.filter((i) => i.product_id !== productId);
  renderCart();
}

function renderCart() {
  const tbody = document.getElementById("cartTableBody");
  const cartEmpty = document.getElementById("cartEmptyState");
  const cartCount = document.getElementById("cartItemsCount");

  if (cartCount) cartCount.innerText = cart.length;

  if (cart.length === 0) {
    if (tbody) tbody.innerHTML = "";
    if (cartEmpty) cartEmpty.style.display = "block";
    resetFinancials();
    return;
  }

  if (cartEmpty) cartEmpty.style.display = "none";

  let html = "";
  cart.forEach((item, index) => {
    const lineSubtotal = item.selling_price * item.quantity;
    html += `
      <tr>
        <td style="font-weight: 600;">
          ${escapeHtml(item.name)}
          <div style="font-size: 0.75rem; color: #64748b;">${item.product_code} | GST ${item.gst_rate}%</div>
        </td>
        <td style="font-weight: 500;">Rs. ${item.selling_price.toFixed(2)}</td>
        <td>
          <div class="qty-control">
            <button type="button" class="qty-btn" onclick="updateQuantity(${item.product_id}, -1)">-</button>
            <span class="qty-input">${item.quantity}</span>
            <button type="button" class="qty-btn" onclick="updateQuantity(${item.product_id}, 1)">+</button>
          </div>
        </td>
        <td style="font-weight: 700; text-align: right;">Rs. ${lineSubtotal.toFixed(2)}</td>
        <td style="text-align: center;">
          <button type="button" class="btn btn-sm btn-secondary" style="color: #ef4444; border: none;" onclick="removeFromCart(${item.product_id})">
            ✕
          </button>
        </td>
      </tr>
    `;
  });

  if (tbody) tbody.innerHTML = html;

  // Compute live calculations from server
  fetchCalculations();
}

function resetFinancials() {
  currentFinancials = {
    gross_subtotal: 0.0,
    total_qty_discount: 0.0,
    bill_disc_amt: 0.0,
    bill_disc_rate: 0.0,
    total_discount: 0.0,
    overall_taxable: 0.0,
    total_gst: 0.0,
    grand_total: 0.0
  };
  updateSummaryUI();
}

function fetchCalculations() {
  const payload = {
    items: cart.map((i) => ({ product_id: i.product_id, quantity: i.quantity }))
  };

  fetch("/api/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then((res) => res.json())
    .then((data) => {
      currentFinancials = data;
      updateSummaryUI();
    })
    .catch((err) => console.error("Calculation error:", err));
}

function updateSummaryUI() {
  const subtotalEl = document.getElementById("summarySubtotal");
  const qtyDiscRow = document.getElementById("summaryQtyDiscRow");
  const qtyDiscEl = document.getElementById("summaryQtyDiscount");
  const billDiscRow = document.getElementById("summaryBillDiscRow");
  const billDiscEl = document.getElementById("summaryBillDiscount");
  const billDiscLabel = document.getElementById("summaryBillDiscLabel");
  const totalDiscEl = document.getElementById("summaryTotalDiscount");
  const taxableEl = document.getElementById("summaryTaxable");
  const gstEl = document.getElementById("summaryGST");
  const grandTotalEl = document.getElementById("summaryGrandTotal");

  if (subtotalEl) subtotalEl.innerText = `Rs. ${currentFinancials.gross_subtotal.toFixed(2)}`;
  
  if (qtyDiscRow) {
    if (currentFinancials.total_qty_discount > 0) {
      qtyDiscRow.style.display = "flex";
      if (qtyDiscEl) qtyDiscEl.innerText = `-Rs. ${currentFinancials.total_qty_discount.toFixed(2)}`;
    } else {
      qtyDiscRow.style.display = "none";
    }
  }

  if (billDiscRow) {
    if (currentFinancials.bill_disc_amt > 0) {
      billDiscRow.style.display = "flex";
      if (billDiscLabel) billDiscLabel.innerText = `Store Offer (${currentFinancials.bill_disc_rate}% Off)`;
      if (billDiscEl) billDiscEl.innerText = `-Rs. ${currentFinancials.bill_disc_amt.toFixed(2)}`;
    } else {
      billDiscRow.style.display = "none";
    }
  }

  if (totalDiscEl) totalDiscEl.innerText = `-Rs. ${currentFinancials.total_discount.toFixed(2)}`;
  if (taxableEl) taxableEl.innerText = `Rs. ${currentFinancials.overall_taxable.toFixed(2)}`;
  if (gstEl) gstEl.innerText = `Rs. ${currentFinancials.total_gst.toFixed(2)}`;
  if (grandTotalEl) grandTotalEl.innerText = `Rs. ${currentFinancials.grand_total.toFixed(2)}`;

  updateChangeDue();
}

function updateChangeDue() {
  const cashInput = document.getElementById("cashGivenInput");
  const changeEl = document.getElementById("changeDueDisplay");
  const changeRow = document.getElementById("changeDueRow");

  if (selectedPaymentMode !== "Cash") {
    if (changeRow) changeRow.style.display = "none";
    return;
  }

  if (changeRow) changeRow.style.display = "flex";

  const cash = parseFloat(cashInput ? cashInput.value : 0) || 0;
  const change = cash - currentFinancials.grand_total;

  if (changeEl) {
    if (change >= 0) {
      changeEl.innerText = `Rs. ${change.toFixed(2)}`;
      changeEl.style.color = "#10b981";
    } else {
      changeEl.innerText = `Short by Rs. ${Math.abs(change).toFixed(2)}`;
      changeEl.style.color = "#ef4444";
    }
  }
}

function handleCheckout() {
  const custName = document.getElementById("custNameInput").value.trim();
  const custPhone = document.getElementById("custPhoneInput").value.trim();
  const custEmail = document.getElementById("custEmailInput") ? document.getElementById("custEmailInput").value.trim() : "";

  if (cart.length === 0) {
    alert("Please add at least one item to the cart.");
    return;
  }

  if (!custName) {
    alert("Please enter customer name.");
    document.getElementById("custNameInput").focus();
    return;
  }

  const phoneClean = custPhone.replace(/[\s-]/g, "");
  if (!/^\d{10}$/.test(phoneClean)) {
    alert("Please enter a valid 10-digit mobile number.");
    document.getElementById("custPhoneInput").focus();
    return;
  }

  let amountPaid = currentFinancials.grand_total;
  let paymentRef = "";

  if (selectedPaymentMode === "Cash") {
    const cashInput = document.getElementById("cashGivenInput");
    amountPaid = parseFloat(cashInput ? cashInput.value : 0) || 0;
    if (amountPaid < currentFinancials.grand_total) {
      alert(`Insufficient cash! Customer must provide at least Rs. ${currentFinancials.grand_total.toFixed(2)}.`);
      return;
    }
  } else if (selectedPaymentMode === "UPI") {
    const upiRef = document.getElementById("upiRefInput");
    paymentRef = upiRef && upiRef.value.trim() ? upiRef.value.trim() : "UPI-" + Date.now().toString().slice(-8);
  } else if (selectedPaymentMode === "Card") {
    const cardLast4 = document.getElementById("cardLast4Input");
    paymentRef = cardLast4 && cardLast4.value.trim() ? "CARD-XXXX-" + cardLast4.value.trim() : "CARD-AUTH-" + Date.now().toString().slice(-6);
  }

  const checkoutPayload = {
    customer_name: custName,
    customer_phone: phoneClean,
    customer_email: custEmail,
    payment_mode: selectedPaymentMode,
    amount_paid: amountPaid,
    payment_ref: paymentRef,
    items: cart.map((i) => ({ product_id: i.product_id, quantity: i.quantity }))
  };

  const btn = document.getElementById("btnCheckout");
  if (btn) {
    btn.disabled = true;
    btn.innerText = "Processing Sale...";
  }

  fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(checkoutPayload)
  })
    .then((res) => res.json())
    .then((res) => {
      if (btn) {
        btn.disabled = false;
        btn.innerText = "Complete Sale & Print Invoice";
      }

      if (!res.success) {
        alert("Checkout Error: " + res.error);
        return;
      }

      // Display receipt modal
      renderReceiptModal(res.bill);

      // Reset cart and customer inputs
      cart = [];
      renderCart();
      document.getElementById("custNameInput").value = "";
      document.getElementById("custPhoneInput").value = "";
      if (document.getElementById("custEmailInput")) document.getElementById("custEmailInput").value = "";
      if (document.getElementById("cashGivenInput")) document.getElementById("cashGivenInput").value = "";
      if (document.getElementById("upiRefInput")) document.getElementById("upiRefInput").value = "";
      if (document.getElementById("cardLast4Input")) document.getElementById("cardLast4Input").value = "";
    })
    .catch((err) => {
      if (btn) {
        btn.disabled = false;
        btn.innerText = "Complete Sale & Print Invoice";
      }
      console.error("Checkout failed:", err);
      alert("Checkout connection failed: " + err);
    });
}

function renderReceiptModal(bill) {
  const container = document.getElementById("receiptModalContent");
  if (!container) return;

  let itemsHtml = "";
  bill.items.forEach((item) => {
    itemsHtml += `
      <tr>
        <td style="padding: 4px 0;">${escapeHtml(item.product_name)} (${item.product_code})</td>
        <td style="text-align: center;">${item.quantity}</td>
        <td style="text-align: right;">${item.selling_price.toFixed(2)}</td>
        <td style="text-align: right;">${item.gst_rate}%</td>
        <td style="text-align: right; font-weight: bold;">${item.item_total.toFixed(2)}</td>
      </tr>
    `;
  });

  let alertsHtml = "";
  if (bill.alerts && bill.alerts.length > 0) {
    alertsHtml = `
      <div style="margin-top: 14px; padding: 8px 12px; background: #fffbeb; border: 1px solid #f59e0b; border-radius: 6px; font-size: 0.8rem; font-family: sans-serif;">
        <strong>Stock Warning:</strong>
        <ul style="margin: 4px 0 0 16px;">
          ${bill.alerts.map((a) => `<li>${escapeHtml(a)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="receipt-paper" id="printableReceipt">
      <div class="receipt-header">
        <h3>SMARTBILL</h3>
        <p style="font-size: 0.8rem; margin-top: 2px;">SMART STORE BILLING & INVENTORY SYSTEM</p>
        <p style="font-size: 0.75rem; color: #555;">123 College Road, Silicon Corridor | Phone: +91 98765 43210</p>
        <p style="font-size: 0.72rem; color: #555;">GSTIN: 29ABCDE1234F1Z5</p>
      </div>

      <div class="receipt-divider"></div>

      <div style="font-size: 0.8rem; display: flex; justify-content: space-between;">
        <span><strong>Bill No:</strong> ${bill.bill_no}</span>
        <span><strong>Date:</strong> ${bill.date}</span>
      </div>
      <div style="font-size: 0.8rem; display: flex; justify-content: space-between; margin-top: 2px;">
        <span><strong>Customer:</strong> ${escapeHtml(bill.customer_name)}</span>
        <span><strong>Time:</strong> ${bill.time}</span>
      </div>
      <div style="font-size: 0.8rem; margin-top: 2px;">
        <span><strong>Phone:</strong> ${bill.customer_phone}</span>
      </div>

      <div class="receipt-divider"></div>

      <table class="receipt-table">
        <thead>
          <tr>
            <th>Item</th>
            <th style="text-align: center;">Qty</th>
            <th style="text-align: right;">Price</th>
            <th style="text-align: right;">GST</th>
            <th style="text-align: right;">Total</th>
          </tr>
        </thead>
        <tbody>
          ${itemsHtml}
        </tbody>
      </table>

      <div class="receipt-divider"></div>

      <div class="receipt-totals-row">
        <span>Gross Subtotal</span>
        <span>Rs. ${bill.subtotal.toFixed(2)}</span>
      </div>

      ${
        bill.discount_breakdown.qty_discount > 0
          ? `<div class="receipt-totals-row" style="color: #059669;">
              <span>Quantity Bulk Discount</span>
              <span>-Rs. ${bill.discount_breakdown.qty_discount.toFixed(2)}</span>
            </div>`
          : ""
      }

      ${
        bill.discount_breakdown.bill_discount > 0
          ? `<div class="receipt-totals-row" style="color: #059669;">
              <span>Store Offer (${bill.discount_breakdown.bill_discount_rate}% Off)</span>
              <span>-Rs. ${bill.discount_breakdown.bill_discount.toFixed(2)}</span>
            </div>`
          : ""
      }

      <div class="receipt-totals-row">
        <span>Total Discount</span>
        <span>-Rs. ${bill.discount_breakdown.total_discount.toFixed(2)}</span>
      </div>

      <div class="receipt-totals-row">
        <span>Net Taxable Value</span>
        <span>Rs. ${bill.taxable_amount.toFixed(2)}</span>
      </div>

      <div class="receipt-totals-row">
        <span>Total GST Amount</span>
        <span>Rs. ${bill.total_gst.toFixed(2)}</span>
      </div>

      <div class="receipt-totals-row receipt-grand-total">
        <span>GRAND TOTAL</span>
        <span>Rs. ${bill.grand_total.toFixed(2)}</span>
      </div>

      <div class="receipt-totals-row">
        <span>Payment Mode</span>
        <span>${bill.payment_mode}</span>
      </div>
      <div class="receipt-totals-row">
        <span>Amount Paid</span>
        <span>Rs. ${bill.amount_paid.toFixed(2)}</span>
      </div>
      ${
        bill.payment_mode === "Cash"
          ? `<div class="receipt-totals-row" style="font-weight: bold;">
              <span>Change Due</span>
              <span>Rs. ${bill.change_due.toFixed(2)}</span>
            </div>`
          : ""
      }
      ${
        bill.payment_ref
          ? `<div class="receipt-totals-row" style="font-size: 0.75rem;">
              <span>Payment Ref</span>
              <span>${escapeHtml(bill.payment_ref)}</span>
            </div>`
          : ""
      }

      <div class="receipt-divider"></div>

      <div style="text-align: center; font-size: 0.8rem; margin-top: 10px;">
        <p><strong>Thank You for Shopping with SmartBill!</strong></p>
        <p style="font-size: 0.72rem; color: #555; margin-top: 2px;">Please preserve this receipt for warranty and returns.</p>
      </div>

      ${alertsHtml}
    </div>
  `;

  openModal("receiptModal");
}

function printReceipt() {
  window.print();
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
