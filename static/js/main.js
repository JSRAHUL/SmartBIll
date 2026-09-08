/**
 * SmartBill - Global Client JavaScript
 */

document.addEventListener("DOMContentLoaded", () => {
  // Mobile sidebar toggle
  const menuBtn = document.getElementById("mobileMenuBtn");
  const sidebar = document.querySelector(".sidebar");

  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  // Close modals when clicking backdrop
  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove("show");
      }
    });
  });

  // Modal close buttons
  document.querySelectorAll(".modal-close, [data-modal-close]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal-backdrop");
      if (modal) modal.classList.remove("show");
    });
  });
});

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add("show");
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("show");
}

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `badge badge-${type === 'error' ? 'danger' : type}`;
  toast.style.cssText = "padding: 12px 18px; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 8px; border-radius: 8px;";
  toast.innerText = message;

  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3500);
}
