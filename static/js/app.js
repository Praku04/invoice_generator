// Main application JavaScript

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set active navigation
    setActiveNavigation();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Check authentication status
    checkAuthStatus();
}

function setActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

function checkAuthStatus() {
    const token = getToken();
    const currentPath = window.location.pathname;
    
    // Protected routes
    const protectedRoutes = ['/dashboard', '/invoices', '/settings', '/subscription'];
    const authRoutes = ['/login', '/register'];
    
    if (protectedRoutes.some(route => currentPath.startsWith(route))) {
        if (!token) {
            window.location.href = '/login';
            return;
        }
        
        // Verify token validity
        verifyToken(token);
    }
    
    if (authRoutes.includes(currentPath) && token) {
        window.location.href = '/dashboard';
    }
}

async function verifyToken(token) {
    try {
        const response = await apiRequest('/users/me');
        if (!response.ok) {
            removeToken();
            window.location.href = '/login';
        }
    } catch (error) {
        removeToken();
        window.location.href = '/login';
    }
}

// Invoice management functions
class InvoiceManager {
    constructor() {
        this.items = [];
        this.itemCounter = 0;
    }
    
    addItem(itemData = {}) {
        const item = {
            id: ++this.itemCounter,
            item_name: itemData.item_name || '',
            description: itemData.description || '',
            hsn_code: itemData.hsn_code || '',
            quantity: itemData.quantity || 1,
            unit: itemData.unit || 'Nos',
            rate: itemData.rate || 0,
            discount_percentage: itemData.discount_percentage || 0,
            discount_amount: itemData.discount_amount || 0,
            gst_rate: itemData.gst_rate || 0
        };
        
        this.items.push(item);
        this.renderItems();
        this.calculateTotals();
    }
    
    removeItem(itemId) {
        this.items = this.items.filter(item => item.id !== itemId);
        this.renderItems();
        this.calculateTotals();
    }
    
    updateItem(itemId, field, value) {
        const item = this.items.find(item => item.id === itemId);
        if (item) {
            item[field] = value;
            this.calculateItemTotals(item);
            this.calculateTotals();
        }
    }
    
    calculateItemTotals(item) {
        const lineTotal = item.quantity * item.rate;
        const discountAmount = item.discount_percentage > 0 
            ? lineTotal * (item.discount_percentage / 100)
            : item.discount_amount;
        const taxableAmount = lineTotal - discountAmount;
        const gstAmount = taxableAmount * (item.gst_rate / 100);
        const totalAmount = taxableAmount + gstAmount;
        
        item.line_total = lineTotal;
        item.discount_amount = discountAmount;
        item.taxable_amount = taxableAmount;
        item.gst_amount = gstAmount;
        item.total_amount = totalAmount;
    }
    
    calculateTotals() {
        const subtotal = this.items.reduce((sum, item) => sum + (item.line_total || 0), 0);
        const totalDiscount = this.items.reduce((sum, item) => sum + (item.discount_amount || 0), 0);
        const taxableAmount = subtotal - totalDiscount;
        const totalTax = this.items.reduce((sum, item) => sum + (item.gst_amount || 0), 0);
        const grandTotal = taxableAmount + totalTax;
        
        this.updateTotalsDisplay({
            subtotal,
            totalDiscount,
            taxableAmount,
            totalTax,
            grandTotal
        });
    }
    
    updateTotalsDisplay(totals) {
        const elements = {
            subtotal: document.getElementById('subtotal'),
            totalDiscount: document.getElementById('totalDiscount'),
            taxableAmount: document.getElementById('taxableAmount'),
            totalTax: document.getElementById('totalTax'),
            grandTotal: document.getElementById('grandTotal')
        };
        
        Object.keys(elements).forEach(key => {
            if (elements[key]) {
                elements[key].textContent = formatCurrency(totals[key]);
            }
        });
    }
    
    renderItems() {
        const container = document.getElementById('invoiceItems');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.items.forEach(item => {
            const itemRow = this.createItemRow(item);
            container.appendChild(itemRow);
        });
    }
    
    createItemRow(item) {
        const row = document.createElement('div');
        row.className = 'invoice-item-row';
        row.innerHTML = `
            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label">Item Name</label>
                    <input type="text" class="form-control" value="${item.item_name}" 
                           onchange="invoiceManager.updateItem(${item.id}, 'item_name', this.value)">
                </div>
                <div class="col-md-2">
                    <label class="form-label">Quantity</label>
                    <input type="number" class="form-control" value="${item.quantity}" step="0.001"
                           onchange="invoiceManager.updateItem(${item.id}, 'quantity', parseFloat(this.value))">
                </div>
                <div class="col-md-2">
                    <label class="form-label">Rate</label>
                    <input type="number" class="form-control" value="${item.rate}" step="0.01"
                           onchange="invoiceManager.updateItem(${item.id}, 'rate', parseFloat(this.value))">
                </div>
                <div class="col-md-2">
                    <label class="form-label">GST %</label>
                    <select class="form-select" onchange="invoiceManager.updateItem(${item.id}, 'gst_rate', parseFloat(this.value))">
                        <option value="0" ${item.gst_rate === 0 ? 'selected' : ''}>0%</option>
                        <option value="5" ${item.gst_rate === 5 ? 'selected' : ''}>5%</option>
                        <option value="12" ${item.gst_rate === 12 ? 'selected' : ''}>12%</option>
                        <option value="18" ${item.gst_rate === 18 ? 'selected' : ''}>18%</option>
                        <option value="28" ${item.gst_rate === 28 ? 'selected' : ''}>28%</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Total</label>
                    <input type="text" class="form-control" value="${formatCurrency(item.total_amount || 0)}" readonly>
                </div>
                <div class="col-md-1">
                    <label class="form-label">&nbsp;</label>
                    <button type="button" class="btn btn-outline-danger w-100" 
                            onclick="invoiceManager.removeItem(${item.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        return row;
    }
    
    getInvoiceData() {
        return {
            items: this.items.map(item => ({
                item_name: item.item_name,
                description: item.description,
                hsn_code: item.hsn_code,
                quantity: item.quantity,
                unit: item.unit,
                rate: item.rate,
                discount_percentage: item.discount_percentage,
                gst_rate: item.gst_rate
            }))
        };
    }
}

// File upload handler
class FileUploadHandler {
    constructor(containerId, fileType) {
        this.container = document.getElementById(containerId);
        this.fileType = fileType;
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        this.container.addEventListener('dragover', this.handleDragOver.bind(this));
        this.container.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.container.addEventListener('drop', this.handleDrop.bind(this));
        this.container.addEventListener('click', this.handleClick.bind(this));
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.container.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.container.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.container.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.uploadFile(files[0]);
        }
    }
    
    handleClick() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            if (e.target.files.length > 0) {
                this.uploadFile(e.target.files[0]);
            }
        };
        input.click();
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(`/api/files/upload/${this.fileType}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getToken()}`
                },
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                this.displayUploadedFile(result);
                showAlert('File uploaded successfully', 'success');
            } else {
                const error = await response.json();
                showAlert(error.detail || 'Upload failed', 'danger');
            }
        } catch (error) {
            showAlert('Network error during upload', 'danger');
        }
    }
    
    displayUploadedFile(fileData) {
        this.container.innerHTML = `
            <div class="uploaded-file">
                <img src="/uploads/${this.fileType}/${fileData.filename}" alt="${fileData.original_filename}">
                <div class="flex-grow-1">
                    <div class="fw-bold">${fileData.original_filename}</div>
                    <small class="text-muted">${(fileData.file_size / 1024).toFixed(1)} KB</small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentElement.parentElement.innerHTML = this.parentElement.parentElement.dataset.originalContent">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
    }
}

// Subscription management
class SubscriptionManager {
    static async subscribe(planId) {
        try {
            const response = await apiRequest('/subscriptions/subscribe', {
                method: 'POST',
                body: JSON.stringify({ plan_id: planId })
            });
            
            if (response.ok) {
                const subscription = await response.json();
                
                if (subscription.razorpay_subscription_id) {
                    // Redirect to Razorpay payment
                    this.initiateRazorpayPayment(subscription);
                } else {
                    // Free plan activated
                    showAlert('Subscription activated successfully', 'success');
                    window.location.reload();
                }
            } else {
                const error = await response.json();
                showAlert(error.detail || 'Subscription failed', 'danger');
            }
        } catch (error) {
            showAlert('Network error during subscription', 'danger');
        }
    }
    
    static initiateRazorpayPayment(subscription) {
        // This would integrate with Razorpay's JavaScript SDK
        // For now, show a placeholder
        showAlert('Redirecting to payment gateway...', 'info');
        
        // In production, you would use:
        // const options = {
        //     key: 'your_razorpay_key_id',
        //     subscription_id: subscription.razorpay_subscription_id,
        //     name: 'Invoice Generator SaaS',
        //     description: 'Pro Plan Subscription',
        //     handler: function(response) {
        //         // Handle successful payment
        //     }
        // };
        // const rzp = new Razorpay(options);
        // rzp.open();
    }
    
    static async cancelSubscription(subscriptionId) {
        if (!confirm('Are you sure you want to cancel your subscription?')) {
            return;
        }
        
        try {
            const response = await apiRequest(`/subscriptions/cancel/${subscriptionId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                showAlert('Subscription cancelled successfully', 'success');
                window.location.reload();
            } else {
                const error = await response.json();
                showAlert(error.detail || 'Cancellation failed', 'danger');
            }
        } catch (error) {
            showAlert('Network error during cancellation', 'danger');
        }
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateGSTIN(gstin) {
    const re = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
    return re.test(gstin);
}

function validatePAN(pan) {
    const re = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return re.test(pan);
}

// Export for global use
window.InvoiceManager = InvoiceManager;
window.FileUploadHandler = FileUploadHandler;
window.SubscriptionManager = SubscriptionManager;