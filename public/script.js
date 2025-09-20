// DonutMarket Frontend JavaScript

// Product data
const products = {
    'DonutSMP Coins': { price: 0.18, unit: '/M' },
    'Elytra': { price: 30.99, unit: '' },
    'Netherite Armor': { price: 19.99, unit: '' },
    'Skeleton Spawner': { price: 0.23, unit: '' },
    'Mystery Box': { price: 5.99, unit: '' }
};

// DOM Elements
const modal = document.getElementById('purchaseModal');
const modalItemName = document.getElementById('modalItemName');
const modalItemPrice = document.getElementById('modalItemPrice');
const closeBtn = document.querySelector('.close');
const quantityInput = document.getElementById('quantity');
const referralCodeInput = document.getElementById('referralCode');
const subtotalSpan = document.getElementById('subtotal');
const discountSpan = document.getElementById('discount');
const totalSpan = document.getElementById('total');

// Current purchase data
let currentProduct = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    addSmoothScrolling();
    addLoadingAnimations();
});

// Initialize all event listeners
function initializeEventListeners() {
    // Product buy buttons
    const buyButtons = document.querySelectorAll('.product-card .btn-primary');
    buyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productCard = this.closest('.product-card');
            const productName = productCard.querySelector('h3').textContent;
            openPurchaseModal(productName);
        });
    });

    // Modal close events
    closeBtn.addEventListener('click', closePurchaseModal);
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            closePurchaseModal();
        }
    });

    // Purchase form events
    quantityInput.addEventListener('input', updateTotal);
    referralCodeInput.addEventListener('input', updateTotal);

    // Purchase form submission
    const purchaseForm = document.querySelector('.purchase-form');
    purchaseForm.addEventListener('submit', handlePurchase);

    // Review form submission
    const reviewForm = document.querySelector('.review-form-content');
    if (reviewForm) {
        reviewForm.addEventListener('submit', handleReviewSubmission);
    }

    // Navigation smooth scrolling
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Open purchase modal
function openPurchaseModal(productName) {
    currentProduct = products[productName];
    if (!currentProduct) return;

    modalItemName.textContent = productName;
    modalItemPrice.textContent = `$${currentProduct.price}${currentProduct.unit}`;
    
    // Reset form
    document.getElementById('username').value = '';
    document.getElementById('referralCode').value = '';
    document.getElementById('quantity').value = '1';
    
    updateTotal();
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close purchase modal
function closePurchaseModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
    currentProduct = null;
}

// Update total calculation
function updateTotal() {
    if (!currentProduct) return;

    const quantity = parseInt(quantityInput.value) || 1;
    const referralCode = referralCodeInput.value.trim();
    
    const subtotal = currentProduct.price * quantity;
    let discount = 0;
    
    // Apply 10% discount if referral code is provided
    if (referralCode) {
        discount = subtotal * 0.1;
    }
    
    const total = subtotal - discount;
    
    subtotalSpan.textContent = subtotal.toFixed(2);
    discountSpan.textContent = discount.toFixed(2);
    totalSpan.textContent = total.toFixed(2);
}

// Handle purchase submission
function handlePurchase(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const username = formData.get('username');
    const referralCode = formData.get('referralCode');
    const quantity = formData.get('quantity');
    
    if (!username) {
        showNotification('Please enter your Minecraft username', 'error');
        return;
    }
    
    // Simulate purchase process
    showNotification('Processing your purchase...', 'info');
    
    setTimeout(() => {
        showNotification('Purchase successful! Check your Discord for delivery details.', 'success');
        closePurchaseModal();
    }, 2000);
}

// Handle review submission
function handleReviewSubmission(e) {
    e.preventDefault();
    
    const textarea = e.target.querySelector('textarea');
    const reviewText = textarea.value.trim();
    
    if (!reviewText) {
        showNotification('Please write a review before submitting', 'error');
        return;
    }
    
    showNotification('Thank you for your review! It will be published after moderation.', 'success');
    textarea.value = '';
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '3000',
        maxWidth: '400px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
        animation: 'slideInRight 0.3s ease'
    });
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.background = 'linear-gradient(135deg, #48bb78, #38a169)';
            break;
        case 'error':
            notification.style.background = 'linear-gradient(135deg, #f56565, #e53e3e)';
            break;
        case 'info':
        default:
            notification.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
            break;
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add smooth scrolling for navigation
function addSmoothScrolling() {
    // Add smooth scrolling CSS if not already present
    if (!document.querySelector('#smooth-scroll-style')) {
        const style = document.createElement('style');
        style.id = 'smooth-scroll-style';
        style.textContent = `
            html {
                scroll-behavior: smooth;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            .fade-in {
                opacity: 0;
                transform: translateY(30px);
                transition: opacity 0.6s ease, transform 0.6s ease;
            }
            
            .fade-in.visible {
                opacity: 1;
                transform: translateY(0);
            }
        `;
        document.head.appendChild(style);
    }
}

// Add loading animations
function addLoadingAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Add fade-in class to elements
    const animatedElements = document.querySelectorAll('.step-card, .product-card, .referral-card, .benefit-card');
    animatedElements.forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });
}

// Simulate loading vouches from Discord
function loadDiscordVouches() {
    const loadingMessage = document.querySelector('.loading-message');
    if (!loadingMessage) return;
    
    setTimeout(() => {
        loadingMessage.innerHTML = `
            <div class="vouches-loaded">
                <h4>Recent Customer Reviews</h4>
                <div class="vouch-item">
                    <span class="vouch-user">@MinecraftPro123</span>
                    <span class="vouch-text">"Fast delivery and great prices! Highly recommended!"</span>
                    <span class="vouch-rating">⭐⭐⭐⭐⭐</span>
                </div>
                <div class="vouch-item">
                    <span class="vouch-user">@DonutFan456</span>
                    <span class="vouch-text">"Got my coins instantly, amazing service!"</span>
                    <span class="vouch-rating">⭐⭐⭐⭐⭐</span>
                </div>
                <div class="vouch-item">
                    <span class="vouch-user">@PvPMaster789</span>
                    <span class="vouch-text">"Best DonutSMP store, will buy again!"</span>
                    <span class="vouch-rating">⭐⭐⭐⭐⭐</span>
                </div>
            </div>
        `;
        
        // Add styles for vouches
        const vouchStyle = document.createElement('style');
        vouchStyle.textContent = `
            .vouches-loaded {
                text-align: left;
                max-width: 600px;
                margin: 0 auto;
            }
            
            .vouches-loaded h4 {
                text-align: center;
                margin-bottom: 1.5rem;
                color: #2d3748;
            }
            
            .vouch-item {
                background: white;
                padding: 1rem;
                margin-bottom: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .vouch-user {
                font-weight: 600;
                color: #667eea;
            }
            
            .vouch-text {
                color: #4a5568;
                font-style: italic;
            }
            
            .vouch-rating {
                font-size: 0.9rem;
            }
        `;
        document.head.appendChild(vouchStyle);
    }, 3000);
}

// Initialize vouch loading
document.addEventListener('DOMContentLoaded', loadDiscordVouches);

// Add cart functionality
let cart = [];

function addToCart(productName, quantity = 1) {
    const existingItem = cart.find(item => item.name === productName);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            name: productName,
            price: products[productName].price,
            quantity: quantity
        });
    }
    
    updateCartDisplay();
    showNotification(`Added ${productName} to cart!`, 'success');
}

function updateCartDisplay() {
    const cartCount = cart.reduce((total, item) => total + item.quantity, 0);
    const cartLink = document.querySelector('.nav-link[href="#cart"]');
    
    if (cartLink) {
        const cartText = cartLink.querySelector('i').nextSibling;
        if (cartCount > 0) {
            cartText.textContent = ` Cart (${cartCount})`;
        } else {
            cartText.textContent = ' Cart';
        }
    }
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modal
    if (e.key === 'Escape' && modal.style.display === 'block') {
        closePurchaseModal();
    }
    
    // Ctrl/Cmd + K to focus search (if implemented)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focus search input if available
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Add mobile menu toggle (if needed)
function initializeMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const hamburger = document.createElement('button');
    hamburger.className = 'mobile-menu-toggle';
    hamburger.innerHTML = '<i class="fas fa-bars"></i>';
    hamburger.style.display = 'none';
    
    // Add hamburger to nav
    const navContainer = document.querySelector('.nav-container');
    navContainer.appendChild(hamburger);
    
    hamburger.addEventListener('click', function() {
        navLinks.classList.toggle('mobile-open');
    });
    
    // Add mobile styles
    const mobileStyle = document.createElement('style');
    mobileStyle.textContent = `
        @media (max-width: 768px) {
            .mobile-menu-toggle {
                display: block !important;
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
            }
            
            .nav-links {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                flex-direction: column;
                padding: 1rem;
                transform: translateY(-100%);
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }
            
            .nav-links.mobile-open {
                transform: translateY(0);
                opacity: 1;
                visibility: visible;
            }
        }
    `;
    document.head.appendChild(mobileStyle);
}

// Initialize mobile menu
document.addEventListener('DOMContentLoaded', initializeMobileMenu);

// Performance optimization: Lazy load images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', initializeLazyLoading);
