function showOkorCancelModal(message, onOk, onCancel) {
  // すでに表示中なら削除
  const existing = document.getElementById('modalOverlay');
  if (existing) existing.remove();

  // モーダルHTML構築
  const overlay = document.createElement('div');
  overlay.id = 'modalOverlay';
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal">
      <p>${message}</p>
      <div class="modal-buttons">
        <button class="ok-button">OK</button>
        <!-- <button class="cancel-button">キャンセル</button> -->
      </div>
    </div>
  `;

  // イベント設定
  overlay.querySelector('.ok-button').onclick = () => {
    if (typeof onOk === 'function') onOk();
    overlay.remove();
  };
  overlay.querySelector('.cancel-button').onclick = () => {
    overlay.remove();
  };

  // 表示
  document.body.appendChild(overlay);
  overlay.style.display = 'flex';
}


function showToast(message, type = "info", duration = 3000) {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  document.body.appendChild(toast);

  // アニメーション表示
  setTimeout(() => {
    toast.classList.add("show");
  }, 100);

  // 自動で削除
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}


// 商品一覧を取得して表示
async function loadProducts() {
  try {
    const response = await fetch('/api/products');
    const products = await response.json();
    const productList = document.getElementById('productList');
    productList.innerHTML = '';
    
    products.forEach(product => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><input type="checkbox" class="delete-checkbox" value="${product.product_code}"></td>
        <td>${product.product_code}</td>
        <td>${product.product_name}</td>
        <td>${product.sales_target}</td>
      `;
      productList.appendChild(row);
    });

    // チェックボックスのイベントリスナーを設定
    document.querySelectorAll('.delete-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        this.closest('tr').classList.toggle('selected', this.checked);
      });
    });
  } catch (error) {
    console.error('商品一覧の取得に失敗しました:', error);
  }
}
