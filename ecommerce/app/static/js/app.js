// ---------- Token / auth helpers ----------
const Auth = {
  getToken() { return localStorage.getItem("token"); },
  setToken(t) { localStorage.setItem("token", t); },
  clear() { localStorage.removeItem("token"); localStorage.removeItem("user"); },
  getUser() {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(u) { localStorage.setItem("user", JSON.stringify(u)); },
  isLoggedIn() { return !!this.getToken(); },
};

// ---------- API client ----------
async function api(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = Auth.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = "Something went wrong";
    try {
      const errJson = await res.json();
      detail = errJson.detail || detail;
    } catch (e) {}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ---------- Toast ----------
function showToast(message) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 2200);
}

// ---------- Currency ----------
function formatINR(amount) {
  return "₹" + Number(amount).toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

// ---------- Cart badge ----------
async function refreshCartBadge() {
  const badgeEls = document.querySelectorAll(".cart-badge");
  if (!Auth.isLoggedIn()) {
    badgeEls.forEach((el) => (el.textContent = "0"));
    return;
  }
  try {
    const items = await api("/api/cart", { auth: true });
    const count = items.reduce((sum, i) => sum + i.quantity, 0);
    badgeEls.forEach((el) => (el.textContent = count));
  } catch (e) {
    // token might be invalid/expired
  }
}

async function addToCart(productId, quantity = 1) {
  if (!Auth.isLoggedIn()) {
    showToast("Please log in to add items to cart");
    setTimeout(() => (window.location.href = "/login"), 900);
    return;
  }
  try {
    await api("/api/cart", { method: "POST", auth: true, body: { product_id: productId, quantity } });
    showToast("Added to cart");
    refreshCartBadge();
  } catch (e) {
    showToast(e.message);
  }
}

// ---------- Product card renderer (shared across pages) ----------
function productCardHTML(p) {
  const offBadge = p.discount_percent > 0
    ? `<span class="discount-badge">-${p.discount_percent}%</span>`
    : "";
  return `
    <div class="product-card" data-id="${p.id}">
      <a href="/product/${p.id}">
        <div class="product-img-wrap">
          <img src="${p.image_url}" alt="${escapeHTML(p.title)}" loading="lazy" />
          ${offBadge}
        </div>
      </a>
      <button class="wishlist-btn" aria-label="Add to wishlist" onclick="event.stopPropagation(); this.classList.toggle('active'); this.querySelector('i').className = this.classList.contains('active') ? 'ti ti-heart-filled' : 'ti ti-heart';">
        <i class="ti ti-heart"></i>
      </button>
      <div class="product-info">
        <a href="/product/${p.id}">
          <p class="product-brand">${escapeHTML(p.brand || "")}</p>
          <p class="product-title">${escapeHTML(p.title)}</p>
        </a>
        <div class="product-price-row">
          <span class="price-now">${formatINR(p.price)}</span>
          ${p.mrp > p.price ? `<span class="price-mrp">${formatINR(p.mrp)}</span>` : ""}
          ${p.discount_percent > 0 ? `<span class="price-off">${p.discount_percent}% off</span>` : ""}
        </div>
        <div>
          <span class="rating-pill">${Number(p.rating).toFixed(1)} <i class="ti ti-star-filled" style="font-size:9px"></i></span>
          <span class="rating-count">${p.rating_count.toLocaleString("en-IN")}</span>
        </div>
      </div>
    </div>
  `;
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

// ---------- Header auth state ----------
function renderHeaderAuthState() {
  const accountEl = document.getElementById("account-action");
  if (!accountEl) return;
  const user = Auth.getUser();
  if (user) {
    accountEl.innerHTML = `<i class="ti ti-user"></i><span>${escapeHTML(user.name.split(" ")[0])}</span>`;
    accountEl.onclick = () => {
      if (confirm("Log out of ShopKart?")) {
        Auth.clear();
        window.location.href = "/";
      }
    };
  }
}

document.addEventListener("DOMContentLoaded", () => {
  refreshCartBadge();
  renderHeaderAuthState();
});
