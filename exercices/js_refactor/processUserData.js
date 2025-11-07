// dashboard.js - Gestion du dashboard utilisateur

let userData = null;
let orders = [];
let products = [];
let analytics = {};
let isDarkMode = false;
let isLoading = false;
let currentPage = 1;
let itemsPerPage = 10;
let sortBy = 'date';
let sortOrder = 'desc';
let filters = {
  status: 'all',
  dateFrom: null,
  dateTo: null,
  minAmount: 0,
  maxAmount: 10000
};

function initDashboard() {
  console.log('Initializing dashboard...');
  
  // Charger les données utilisateur
  fetch('https://api.example.com/user/profile')
    .then(response => response.json())
    .then(data => {
      userData = data;
      document.getElementById('username').textContent = data.name;
      document.getElementById('userEmail').textContent = data.email;
      document.getElementById('userAvatar').src = data.avatar || 'default-avatar.png';
      
      if (data.role === 'admin') {
        document.getElementById('adminPanel').style.display = 'block';
      }
      
      if (data.notifications && data.notifications.length > 0) {
        document.getElementById('notifBadge').textContent = data.notifications.length;
        document.getElementById('notifBadge').style.display = 'inline-block';
      }
      
      if (data.premium) {
        document.getElementById('premiumBadge').style.display = 'inline-block';
      }
    })
    .catch(error => {
      console.error('Error loading user data:', error);
      showError('Impossible de charger les données utilisateur');
    });
  
  // Charger les commandes
  isLoading = true;
  document.getElementById('loadingSpinner').style.display = 'block';
  
  fetch('https://api.example.com/orders?page=' + currentPage + '&limit=' + itemsPerPage + '&sort=' + sortBy + '&order=' + sortOrder)
    .then(response => response.json())
    .then(data => {
      orders = data.orders;
      isLoading = false;
      document.getElementById('loadingSpinner').style.display = 'none';
      
      let ordersList = document.getElementById('ordersList');
      ordersList.innerHTML = '';
      
      for (let i = 0; i < orders.length; i++) {
        let order = orders[i];
        let orderDiv = document.createElement('div');
        orderDiv.className = 'order-item';
        orderDiv.id = 'order-' + order.id;
        
        let statusClass = '';
        if (order.status === 'pending') {
          statusClass = 'status-pending';
        } else if (order.status === 'shipped') {
          statusClass = 'status-shipped';
        } else if (order.status === 'delivered') {
          statusClass = 'status-delivered';
        } else if (order.status === 'cancelled') {
          statusClass = 'status-cancelled';
        }
        
        let orderDate = new Date(order.createdAt);
        let formattedDate = orderDate.getDate() + '/' + (orderDate.getMonth() + 1) + '/' + orderDate.getFullYear();
        
        orderDiv.innerHTML = `
          <div class="order-header">
            <span class="order-id">#${order.id}</span>
            <span class="order-date">${formattedDate}</span>
            <span class="order-status ${statusClass}">${order.status}</span>
          </div>
          <div class="order-details">
            <p>Total: ${order.total}€</p>
            <p>Articles: ${order.items.length}</p>
          </div>
          <button onclick="viewOrderDetails(${order.id})">Voir détails</button>
        `;
        
        ordersList.appendChild(orderDiv);
      }
      
      // Pagination
      let totalPages = Math.ceil(data.total / itemsPerPage);
      let paginationDiv = document.getElementById('pagination');
      paginationDiv.innerHTML = '';
      
      if (currentPage > 1) {
        let prevBtn = document.createElement('button');
        prevBtn.textContent = 'Précédent';
        prevBtn.onclick = function() {
          currentPage--;
          initDashboard();
        };
        paginationDiv.appendChild(prevBtn);
      }
      
      for (let i = 1; i <= totalPages; i++) {
        let pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        if (i === currentPage) {
          pageBtn.className = 'active';
        }
        pageBtn.onclick = function() {
          currentPage = i;
          initDashboard();
        };
        paginationDiv.appendChild(pageBtn);
      }
      
      if (currentPage < totalPages) {
        let nextBtn = document.createElement('button');
        nextBtn.textContent = 'Suivant';
        nextBtn.onclick = function() {
          currentPage++;
          initDashboard();
        };
        paginationDiv.appendChild(nextBtn);
      }
    })
    .catch(error => {
      console.error('Error loading orders:', error);
      isLoading = false;
      document.getElementById('loadingSpinner').style.display = 'none';
      showError('Impossible de charger les commandes');
    });
  
  // Charger les produits
  fetch('https://api.example.com/products')
    .then(response => response.json())
    .then(data => {
      products = data.products;
      
      let productGrid = document.getElementById('productGrid');
      productGrid.innerHTML = '';
      
      for (let i = 0; i < products.length; i++) {
        let product = products[i];
        
        if (filters.status !== 'all' && product.status !== filters.status) {
          continue;
        }
        
        let productCard = document.createElement('div');
        productCard.className = 'product-card';
        
        let discountBadge = '';
        if (product.discount && product.discount > 0) {
          discountBadge = `<span class="discount-badge">-${product.discount}%</span>`;
        }
        
        let stockStatus = '';
        if (product.stock === 0) {
          stockStatus = '<span class="out-of-stock">Rupture de stock</span>';
        } else if (product.stock < 5) {
          stockStatus = '<span class="low-stock">Stock limité</span>';
        }
        
        productCard.innerHTML = `
          <div class="product-image">
            <img src="${product.image}" alt="${product.name}">
            ${discountBadge}
          </div>
          <div class="product-info">
            <h3>${product.name}</h3>
            <p class="product-description">${product.description}</p>
            <div class="product-price">
              <span class="current-price">${product.price}€</span>
              ${product.originalPrice ? `<span class="original-price">${product.originalPrice}€</span>` : ''}
            </div>
            ${stockStatus}
            <button onclick="addToCart(${product.id})" ${product.stock === 0 ? 'disabled' : ''}>
              Ajouter au panier
            </button>
          </div>
        `;
        
        productGrid.appendChild(productCard);
      }
    })
    .catch(error => {
      console.error('Error loading products:', error);
      showError('Impossible de charger les produits');
    });
  
  // Charger les analytics
  fetch('https://api.example.com/analytics')
    .then(response => response.json())
    .then(data => {
      analytics = data;
      
      document.getElementById('totalOrders').textContent = data.totalOrders;
      document.getElementById('totalRevenue').textContent = data.totalRevenue + '€';
      document.getElementById('avgOrderValue').textContent = data.avgOrderValue + '€';
      document.getElementById('totalCustomers').textContent = data.totalCustomers;
      
      // Graphique des ventes
      let salesChart = document.getElementById('salesChart');
      let maxSales = Math.max(...data.monthlySales);
      
      salesChart.innerHTML = '';
      
      for (let i = 0; i < data.monthlySales.length; i++) {
        let month = data.monthlySales[i];
        let barHeight = (month.value / maxSales) * 200;
        
        let bar = document.createElement('div');
        bar.className = 'chart-bar';
        bar.style.height = barHeight + 'px';
        bar.innerHTML = `
          <div class="bar-value">${month.value}€</div>
          <div class="bar-label">${month.month}</div>
        `;
        
        salesChart.appendChild(bar);
      }
      
      // Top produits
      let topProductsList = document.getElementById('topProductsList');
      topProductsList.innerHTML = '';
      
      for (let i = 0; i < data.topProducts.length; i++) {
        let product = data.topProducts[i];
        let li = document.createElement('li');
        li.innerHTML = `
          <span class="product-name">${product.name}</span>
          <span class="product-sales">${product.sales} ventes</span>
        `;
        topProductsList.appendChild(li);
      }
    })
    .catch(error => {
      console.error('Error loading analytics:', error);
      showError('Impossible de charger les statistiques');
    });
}

function viewOrderDetails(orderId) {
  console.log('Viewing order details for:', orderId);
  
  fetch('https://api.example.com/orders/' + orderId)
    .then(response => response.json())
    .then(order => {
      let modal = document.getElementById('orderModal');
      let modalContent = document.getElementById('orderModalContent');
      
      let orderDate = new Date(order.createdAt);
      let formattedDate = orderDate.getDate() + '/' + (orderDate.getMonth() + 1) + '/' + orderDate.getFullYear();
      
      let itemsHtml = '';
      for (let i = 0; i < order.items.length; i++) {
        let item = order.items[i];
        itemsHtml += `
          <div class="order-item-detail">
            <img src="${item.image}" alt="${item.name}">
            <div class="item-info">
              <h4>${item.name}</h4>
              <p>Quantité: ${item.quantity}</p>
              <p>Prix unitaire: ${item.price}€</p>
              <p>Sous-total: ${item.quantity * item.price}€</p>
            </div>
          </div>
        `;
      }
      
      let shippingCost = order.shippingCost || 0;
      let taxAmount = order.total * 0.2;
      let subtotal = order.total - shippingCost - taxAmount;
      
      modalContent.innerHTML = `
        <h2>Commande #${order.id}</h2>
        <div class="order-info">
          <p><strong>Date:</strong> ${formattedDate}</p>
          <p><strong>Statut:</strong> ${order.status}</p>
          <p><strong>Adresse de livraison:</strong></p>
          <p>${order.shippingAddress.street}</p>
          <p>${order.shippingAddress.city}, ${order.shippingAddress.zipCode}</p>
          <p>${order.shippingAddress.country}</p>
        </div>
        <div class="order-items">
          <h3>Articles commandés</h3>
          ${itemsHtml}
        </div>
        <div class="order-summary">
          <p>Sous-total: ${subtotal.toFixed(2)}€</p>
          <p>Frais de port: ${shippingCost.toFixed(2)}€</p>
          <p>TVA (20%): ${taxAmount.toFixed(2)}€</p>
          <p><strong>Total: ${order.total.toFixed(2)}€</strong></p>
        </div>
        <div class="order-actions">
          ${order.status === 'pending' ? '<button onclick="cancelOrder(' + order.id + ')">Annuler la commande</button>' : ''}
          ${order.status === 'delivered' ? '<button onclick="reorder(' + order.id + ')">Commander à nouveau</button>' : ''}
          <button onclick="downloadInvoice(' + order.id + ')">Télécharger la facture</button>
        </div>
      `;
      
      modal.style.display = 'block';
    })
    .catch(error => {
      console.error('Error loading order details:', error);
      showError('Impossible de charger les détails de la commande');
    });
}

function addToCart(productId) {
  console.log('Adding product to cart:', productId);
  
  let product = null;
  for (let i = 0; i < products.length; i++) {
    if (products[i].id === productId) {
      product = products[i];
      break;
    }
  }
  
  if (!product) {
    showError('Produit introuvable');
    return;
  }
  
  if (product.stock === 0) {
    showError('Produit en rupture de stock');
    return;
  }
  
  fetch('https://api.example.com/cart/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    },
    body: JSON.stringify({
      productId: productId,
      quantity: 1
    })
  })
    .then(response => response.json())
    .then(data => {
      showSuccess('Produit ajouté au panier');
      
      // Mettre à jour le badge du panier
      let cartBadge = document.getElementById('cartBadge');
      let currentCount = parseInt(cartBadge.textContent) || 0;
      cartBadge.textContent = currentCount + 1;
      cartBadge.style.display = 'inline-block';
      
      // Animation
      cartBadge.classList.add('bounce');
      setTimeout(function() {
        cartBadge.classList.remove('bounce');
      }, 500);
    })
    .catch(error => {
      console.error('Error adding to cart:', error);
      showError('Impossible d\'ajouter le produit au panier');
    });
}

function cancelOrder(orderId) {
  if (!confirm('Êtes-vous sûr de vouloir annuler cette commande ?')) {
    return;
  }
  
  fetch('https://api.example.com/orders/' + orderId + '/cancel', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    }
  })
    .then(response => response.json())
    .then(data => {
      showSuccess('Commande annulée avec succès');
      document.getElementById('orderModal').style.display = 'none';
      initDashboard();
    })
    .catch(error => {
      console.error('Error cancelling order:', error);
      showError('Impossible d\'annuler la commande');
    });
}

function reorder(orderId) {
  console.log('Reordering:', orderId);
  
  fetch('https://api.example.com/orders/' + orderId)
    .then(response => response.json())
    .then(order => {
      let addedCount = 0;
      let failedCount = 0;
      
      for (let i = 0; i < order.items.length; i++) {
        let item = order.items[i];
        
        fetch('https://api.example.com/cart/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('token')
          },
          body: JSON.stringify({
            productId: item.productId,
            quantity: item.quantity
          })
        })
          .then(response => response.json())
          .then(data => {
            addedCount++;
            
            if (addedCount + failedCount === order.items.length) {
              if (failedCount === 0) {
                showSuccess('Tous les articles ont été ajoutés au panier');
              } else {
                showWarning(addedCount + ' articles ajoutés, ' + failedCount + ' indisponibles');
              }
              
              document.getElementById('orderModal').style.display = 'none';
            }
          })
          .catch(error => {
            console.error('Error adding item:', error);
            failedCount++;
            
            if (addedCount + failedCount === order.items.length) {
              showWarning(addedCount + ' articles ajoutés, ' + failedCount + ' indisponibles');
              document.getElementById('orderModal').style.display = 'none';
            }
          });
      }
    })
    .catch(error => {
      console.error('Error reordering:', error);
      showError('Impossible de recommander');
    });
}

function downloadInvoice(orderId) {
  console.log('Downloading invoice for order:', orderId);
  
  fetch('https://api.example.com/orders/' + orderId + '/invoice', {
    headers: {
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    }
  })
    .then(response => response.blob())
    .then(blob => {
      let url = window.URL.createObjectURL(blob);
      let a = document.createElement('a');
      a.href = url;
      a.download = 'facture-' + orderId + '.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      showSuccess('Facture téléchargée');
    })
    .catch(error => {
      console.error('Error downloading invoice:', error);
      showError('Impossible de télécharger la facture');
    });
}

function applyFilters() {
  let statusFilter = document.getElementById('statusFilter').value;
  let dateFromFilter = document.getElementById('dateFromFilter').value;
  let dateToFilter = document.getElementById('dateToFilter').value;
  let minAmountFilter = document.getElementById('minAmountFilter').value;
  let maxAmountFilter = document.getElementById('maxAmountFilter').value;
  
  filters.status = statusFilter;
  filters.dateFrom = dateFromFilter;
  filters.dateTo = dateToFilter;
  filters.minAmount = parseFloat(minAmountFilter) || 0;
  filters.maxAmount = parseFloat(maxAmountFilter) || 10000;
  
  currentPage = 1;
  initDashboard();
}

function resetFilters() {
  document.getElementById('statusFilter').value = 'all';
  document.getElementById('dateFromFilter').value = '';
  document.getElementById('dateToFilter').value = '';
  document.getElementById('minAmountFilter').value = '';
  document.getElementById('maxAmountFilter').value = '';
  
  filters = {
    status: 'all',
    dateFrom: null,
    dateTo: null,
    minAmount: 0,
    maxAmount: 10000
  };
  
  currentPage = 1;
  initDashboard();
}

function sortOrders(field) {
  if (sortBy === field) {
    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
  } else {
    sortBy = field;
    sortOrder = 'desc';
  }
  
  currentPage = 1;
  initDashboard();
}

function toggleDarkMode() {
  isDarkMode = !isDarkMode;
  
  if (isDarkMode) {
    document.body.classList.add('dark-mode');
    localStorage.setItem('darkMode', 'true');
  } else {
    document.body.classList.remove('dark-mode');
    localStorage.setItem('darkMode', 'false');
  }
}

function showError(message) {
  let toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = 'toast error';
  toast.style.display = 'block';
  
  setTimeout(function() {
    toast.style.display = 'none';
  }, 3000);
}

function showSuccess(message) {
  let toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = 'toast success';
  toast.style.display = 'block';
  
  setTimeout(function() {
    toast.style.display = 'none';
  }, 3000);
}

function showWarning(message) {
  let toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = 'toast warning';
  toast.style.display = 'block';
  
  setTimeout(function() {
    toast.style.display = 'none';
  }, 3000);
}

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing...');
  
  // Vérifier le mode sombre sauvegardé
  let savedDarkMode = localStorage.getItem('darkMode');
  if (savedDarkMode === 'true') {
    isDarkMode = true;
    document.body.classList.add('dark-mode');
  }
  
  // Fermer le modal au clic sur la croix
  let closeModal = document.getElementById('closeModal');
  if (closeModal) {
    closeModal.onclick = function() {
      document.getElementById('orderModal').style.display = 'none';
    };
  }
  
  // Fermer le modal au clic en dehors
  window.onclick = function(event) {
    let modal = document.getElementById('orderModal');
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  };
  
  initDashboard();
});